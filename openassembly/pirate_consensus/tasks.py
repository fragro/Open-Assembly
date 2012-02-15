from celery.task import task
import pytz
import datetime
from pyvotecore.schulze_method import SchulzeMethod
from pyvotecore.schulze_stv import SchulzeSTV
from pirate_consensus.models import ConfirmRankedVote, RankedVote, RankedDecision, Consensus, UpDownVote
from collections import defaultdict
from pirate_topics.models import GroupSettings, MyGroup


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

    mygroups = MyGroup.objects.filter(topic=consensus.content_object.parent)
    num_members = mygroups.count()
    if consensus.phase.curphase.nextphase == None:
        #get the group settings
        settings, is_new = GroupSettings.objects.get_or_create(topic=consensus.content_object.parent)
        #iterate decisions made
        consensus.content_object.parent.decisions += 1
        consensus.content_object.parent.save()
        #if this question does not pass consensus we do not accept, however ignore reporting
        #this gives people an opportunity to not agree with the need for the question itself
        consensus.consensus_percent = get_consensus(consensus)
        consensus.reporting_percent = float(UpDownVote.objects.filter(parent=consensus).count()) / float(num_members)
        cons_passed = test_if_passes(consensus.consensus_percent, consensus.reporting_percent, settings, ignore_reporting=False)

        winner = []
        passes = False
        #if we accept all winners no need for ranking
        if consensus.winners is not None:
            #get nominations and ranked votes
            nominations = Consensus.objects.filter(parent_pk=consensus.content_object.pk)
            #currently supports single winner, in the future we check here for multiple winner or single winner
            confirmed = ConfirmRankedVote.objects.filter(parent=consensus, confirm=True)
            ballot_dict = defaultdict(int)
            user_has_ranked = []
            for conf in confirmed:
                user_has_ranked.append(conf.user)
                rv = tuple([i.nom_cons.pk for i in RankedVote.objects.filter(user=conf.user, parent=consensus).order_by('ranked_vote')])
                ballot_dict[rv] += 1
            #for those that didnt rank vote, we can sample from their updownvotes
            for user in [i.user for i in UpDownVote.objects.filter(parent=consensus)]:
                if user not in user_has_ranked:
                    user_ranks = []
                    print nominations
                    for nom in nominations:
                        try:
                            vote = UpDownVote.objects.get(parent=nom, user=user)
                            user_ranks.append(vote)
                        except:
                            print 'novote: ' + str(nom)
                    user_ranks = sorted(user_ranks, key=lambda x: x.vote)
                    user_ranks.reverse()
                    rv = tuple([i.parent.pk for i in user_ranks])
                    ballot_dict[rv] += 1

            #load up the vote dict for python-vote-core
            blist = []
            for k, v in ballot_dict.items():
                ballot = [[i] for i in k]
                if ballot != []:
                    blist.append({'count': v, 'ballot': ballot})
            print 'calc schulze'
            #right now there is only single winner schulze, add mechanism in for multi later on
            noms_passed = False
            if blist != []:
                #scz = SchulzeMethod(blist, ballot_notation="grouping").as_dict()
                scz = SchulzeSTV(blist, required_winners=consensus.winners, ballot_notation="grouping").as_dict()
                print scz
                schulze_winners = scz['winners']
                #make sure it passes consensus also
                for nom in nominations:
                    nom.consensus_percent = get_consensus(nom)
                    nom.reporting_percent = float(UpDownVote.objects.filter(parent=nom).count()) / float(num_members)
                    nom.save()
                    noms_passed = test_if_passes(nom.consensus_percent, nom.reporting_percent, settings, ignore_reporting=True)
                    if noms_passed == True and nom.pk in schulze_winners:
                        passes = True
                        winner.append(nom.pk)
                        print 'set winner via schulze and passing'
            #there was no ranked winner or the ranked winner failed to consense (weird side case), cycle through all and choose
        if passes == False:
            #if this is None, accept all winners
            if consensus.winners == None:
                num_winners = len(nominations)
            else:
                num_winners = consensus.winners
            consensii = []
            for nom in nominations:
                val = (get_consensus(nom), nom)
                consensii.append(val)
                nom.consensus_percent = val[0]
                nom.reporting_percent = float(UpDownVote.objects.filter(parent=nom).count()) / float(num_members)
                nom.save()
            consensii = sorted(consensii, key=lambda x: x[0])
            consensii.reverse()
            for nom_cons, nom in consensii[0:num_winners]:
                ##calculate reporting percentage, the best is the winner
                noms_passed = test_if_passes(nom_cons, nom.reporting_percent, settings, ignore_reporting=True)
                if noms_passed:
                    winner.append(nom.pk)
                    passes = True
                    print 'noms passed ' + str(noms_passed)
        #if we still haven't
        if passes == True and cons_passed == True:
            consensus.phasename = 'pass'
        else:
            consensus.phasename = 'fail'

        #what to do if there is no winner?
        #decision failed, no one voted in time
        rd = RankedDecision(passed=passes and cons_passed,
                winner=winner,
                parent=consensus,
                consensus_percent=consensus.consensus_percent,
                reporting_percent=consensus.reporting_percent,
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
