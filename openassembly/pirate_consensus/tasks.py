from celery.task import task
import pytz
import datetime
from pyvotecore.schulze_method import SchulzeMethod
from pirate_consensus.models import ConfirmRankedVote, RankedVote, RankedDecision, Consensus, UpDownVote
from collections import defaultdict
from pirate_topics.models import GroupSettings


"""
Scheduled phasechange task, moves consensus object from nomination
to voting phase and voting to decision phase. Events should be based
on a timedelta generated at the time of the proposal generation.
"""


def local_tz_to_utc(tz, phase_change_dt):
    dt1 = datetime.datetime.strptime(phase_change_dt, '%Y-%m-%d %H:%M')
    dt1 = tz.localize(dt1)
    return pytz.utc.normalize(dt1)


@task(ignore_result=True)
def add(c):
    c.phase.curphase = c.phase.curphase.nextphase
    c.phasname = c.phase.curphase.phasename
    if c.phase.curphase.nextphase == None:
        c.phase.complete = True
        c.phase.active = False
    c.phase.save()
    c.save()


def get_consensus(consensus):
    consent = UpDownVote.objects.filter(parent=consensus, vote__gt=6).count()
    dissent = UpDownVote.objects.filter(parent=consensus, vote__lt=6).count()
    try:
        cons_perc = float(consent) / float(consent + dissent)
    except:
        print 'consent: ' + str(consent)
        print 'dissent: ' + str(dissent)
        cons_perc = 0.0
    return cons_perc

"""
Run this task on Conesnsu objects attached to questions. Shifts timed decisions.
Also takes care of determining the winners, so this possibly computationally expensive
task is offloaded to the worker
"""


@task(ignore_result=True)
def initiate_nextphase(consensus):
    logger = initiate_nextphase.get_logger()
    logger.info('Initiating Next Phase for: {0}'.format(consensus.content_object.summary))

    consensus.phase.curphase = consensus.phase.curphase.nextphase
    consensus.phasname = consensus.phase.curphase.phasename

    num_members = consensus.content_object.parent.group_members
    if consensus.phase.curphase.nextphase == None:
        #get the group settings
        settings, is_new = GroupSettings.objects.get_or_create(topic=consensus.content_object.parent)

        consensus.content_object.parent.decisions += 1
        consensus.content_object.parent.save()
        #if this question does not pass consensus we do not accept, however ignore reporting
        #this gives people an opportunity to not agree with the need for the question itself
        cons_perc = get_consensus(consensus)
        report_perc = UpDownVote.objects.filter(parent=consensus).count() / num_members
        cons_passed = test_if_passes(cons_perc, report_perc, settings, ignore_reporting=False)

        winner = None
        max_cons = 0.0
        max_report = 0.0
        passes = False
        if cons_passed:
            #currently supports single winner, in the future we check here for multiple winner or single winner
            confirmed = ConfirmRankedVote.objects.filter(parent=consensus, confirm=True)
            ballot_dict = defaultdict(int)
            for conf in confirmed:
                rv = tuple([i.nom_cons.pk for i in RankedVote.objects.filter(user=conf.user, parent=consensus).order_by('ranked_vote')])
                ballot_dict[rv] += 1
            blist = []
            for k, v in ballot_dict.items():
                ballot = [[i] for i in k]
                if ballot != []:
                    blist.append({'count': v, 'ballot': ballot})
            print 'calc schulze'
            #right now there is only single winner schulze, add mechanism in for multi later on
            noms_passed = False
            if blist != []:
                scz = SchulzeMethod(blist, ballot_notation="grouping").as_dict()
                schulze_winner = scz['winner']
                #make sure it passes consensus also
                nom = Consensus.objects.get(pk=schulze_winner)
                max_cons = get_consensus(nom)
                max_report = UpDownVote.objects.filter(parent=nom).count() / num_members
                noms_passed = test_if_passes(max_cons, max_report, settings, ignore_reporting=True)
                if noms_passed == True:
                    passes = True
                    winner = nom.pk
                    print 'set winner via schulze and passing'
            #there was no ranked winner or the ranked winner failed to consense (weird side case), cycle through all and choose
            if passes == False:
                nominations = [i for i in Consensus.objects.filter(parent_pk=consensus.content_object.pk)]

                max_cons = 0.0
                max_report = 0.0
                print nominations
                for nom in nominations:
                    nom_cons = get_consensus(nom)
                    try:
                        nom_report = UpDownVote.objects.filter(parent=nom).count() / num_members
                    except:
                        print nom.content_object
                        print nom.content_object.parent
                    ##calculate reporting percentage, the best is the winner
                    noms_passed = test_if_passes(nom_cons, nom_report, settings, ignore_reporting=True)
                    if nom_cons > max_cons:
                        max_cons = nom_cons
                        max_report = nom_report
                        winner = nom.pk
                        print 'winner: ' + str(winner)
                    if noms_passed:
                        passes = True
                        print 'noms passed' + str(noms_passed)
        if passes == False:
            consensus.phasename = 'fail'
        elif passes == True:
            consensus.phasename = 'pass'

        #what to do if there is no winner?
        #decision failed, no one voted in time
        rd = RankedDecision(passed=passes and cons_passed,
                winner=winner,
                parent=consensus,
                consensus_percent=cons_perc,
                nomination_consensus_percent=max_cons,
                nomination_reporting_percent=max_report,
                reporting_percent=report_perc,
                submit_date=datetime.datetime.now(),
                algorithm='Schulze Method Single Winner')
        rd.save()

        consensus.phase.complete = True
        consensus.phase.active = False
    else:
        initiate_nextphase.apply_async(args=[consensus], eta=consensus.phase.decision_dt)

    consensus.phase.save()
    consensus.save()

    logger.info('Next Phase Transition {0} completed'.format(consensus.content_object.summary))


#Tests to see if these objects pass the consensus/reporting settings of the groups
def test_if_passes(cons_perc, report_perc, settings, ignore_reporting=False):
    if cons_perc >= settings.consensus_percentage:
        if report_perc >= settings.percent_reporting or ignore_reporting:
            return True
    return False
