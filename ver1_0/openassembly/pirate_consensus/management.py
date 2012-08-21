from pirate_consensus.models import UpDownVote, Consensus
from pirate_topics.models import Topic, MyGroup    


for cons in Consensus.objects.all():
    #update reporting percentage
    upvotes = UpDownVote.objects.filter(object_pk=cons.object_pk, vote__gt=6)
    downvotes = UpDownVote.objects.filter(object_pk=cons.object_pk, vote__lt=6)
    try:
        topic = Topic.objects.get(pk=cons.content_object.parent.pk)
        groups = MyGroup.objects.filter(topic=topic)

        try:
            cons.reporting_percent = (upvotes.count() + downvotes.count()) / float(groups.count())
        except:
            cons.reporting_percent = 0.0

        try:
            cons.consensus_percent = upvotes.count() / float(upvotes.count() + downvotes.count())
        except:
            cons.consensus_percent = 0.0
        cons.rating.set_mean()
        cons.save()
    except:
        pass