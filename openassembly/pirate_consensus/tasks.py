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
"""


@task(ignore_result=True)
def initiate_nextphase(consensus):
    logger = initiate_nextphase.get_logger()
    logger.info('Initiating Next Phase for: {0}'.format(consensus.content_object.summary))

    consensus.phase.curphase = consensus.phase.curphase.nextphase
    consensus.phasname = consensus.phase.curphase.phasename
    if consensus.phase.curphase.nextphase == None:

        consensus.content_object.parent.decisions += 1
        consensus.content_object.parent.save()
        #determine if this consensus passes reporting and consensus requirements
        #currently supports single winner
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
        try:
            if blist != []:
                scz = SchulzeMethod(blist, ballot_notation="grouping").as_dict()
                win = scz['winner']
                nominations = [(Consensus.objects.get(pk=win), win)]
                ##calculate consensus percentage
            else:
                win = ''
                nominations = []
                #nominations = [(i, i.win), Consensus.objects.filter(parent=consensus.content_object)]

            settings, is_new = GroupSettings.objects.get_or_create(topic=consensus.content_object.parent)
            passed = False
            for nom_cons, winner in nominations:
                nom_cons_perc = get_consensus(nom_cons)
                cons_perc = get_consensus(consensus)
                ##calculate reporting percentage
                report_perc = UpDownVote.objects.filter(parent=consensus).count() / float(consensus.content_object.parent.group_members)
                nom_report_perc = UpDownVote.objects.filter(parent=nom_cons).count() / float(nom_cons.content_object.parent.parent.group_members)
                if report_perc >= settings.percent_reporting and nom_report_perc >= settings.percent_reporting:
                    if cons_perc >= settings.consensus_percentage and nom_cons_perc >= settings.consensus_percentage:
                        passed = True

                rd = RankedDecision(winner=winner,
                        parent=consensus,
                        consensus_percent=cons_perc,
                        nomination_consensus_percent=nom_cons_perc,
                        nomination_reporting_percent=nom_report_perc,
                        reporting_percent=report_perc,
                        submit_date=datetime.datetime.now(),
                        algorithm='Schulze Method Single Winner')
                rd.save()
            #decision failed, no one voted in time
            if nominations == []:
                rd = RankedDecision(winner=None,
                    parent=consensus,
                    consensus_percent=0.0,
                    nomination_consensus_percent=0.0,
                    nomination_reporting_percent=0.0,
                    reporting_percent=0.0,
                    submit_date=datetime.datetime.now(),
                    algorithm='Schulze Method Single Winner')
        except:
            print 'schulze failed'
            print blist
            raise
        consensus.phase.complete = True
        consensus.phase.active = False
    else:
        initiate_nextphase.apply_async(args=[consensus], eta=consensus.phase.decision_dt)

    consensus.phase.save()
    consensus.save()

    logger.info('Next Phase Transition {0} completed'.format(consensus.content_object.summary))
