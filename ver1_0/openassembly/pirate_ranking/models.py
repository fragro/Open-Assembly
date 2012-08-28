from django.db import models
from pirate_consensus.models import Consensus, UpDownVote
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime
from celery.task import task
from django.utils.translation import ugettext as _
from django.contrib import admin
from pirate_signals.models import vote_created
import math
from pirate_consensus.models import Rating, Spectrum
from tagging.models import Tag, TaggedItem
from django.contrib.auth.models import User
from pirate_forum.models import ForumDimension
from pirate_topics.models import Topic, MyGroup
from redis_func import redis_client
import json


# Create your models here.
class Ranking(models.Model):
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_set_for_%(class)s")
    object_pk = models.CharField(_('object ID'), max_length=100)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    consensus_pk = models.CharField(_('consensus_object ID'), max_length=100)
    dimension = models.CharField(max_length=25)
    score = models.FloatField()

    def __unicode__(self):
        return "%s: %s" % (self.dimension, self.score)

    def save(self, force_insert=False, force_update=False):
        super(Ranking, self).save(force_insert, force_update)
        if self.dimension == 'hot':
            cons = Consensus.objects.get(pk=self.consensus_pk)
            cons.interest = self.score
            cons.save()
        elif self.dimension == 'cont':
            try:
                #object in question should have consensus associated with it
                cons = Consensus.objects.get(pk=self.consensus_pk)
                cons.controversy = self.score
                cons.save()
            except:
                #if not this is in error
                pass


def calc_new(obj):
    return 0


def calc_controversial(dt, spectrum, rating):
    x = 0
    # weighted votes
    mag = 0
    #magnitude of votes
    #compute the mean
    for k, num in spectrum:
        x += k * num
        mag += num
    if mag != 0:
        mean = x / mag
        #compute the sd
        tot = 0
        for k, num in spectrum:
            #TODO: INEFFICIENT, needs better solution
            for i in range(num):
                tot += math.pow((k - mean), 2)
        sd = math.sqrt(tot / mag)
    else:
        mean = 0.0
        sd = 0.0
    try:
        score = sd * math.log(mag) * dt
    except:
        score = 0
    return score


def calc_hot(dt, spectrum, rating):
    #get spectrum list ex: [(-5,246), (-4,45), ... ,(5,121)]
    x = 0
    for k, num in spectrum:
        x += k * num
    r = 0.0
    tot = 0.0

    for k, weight, num in rating:
        r += k * num * weight
        tot += num
    if tot != 0:
        r = r / tot
        #get average rating
    else:
        r = 0.0

    if r != 0:
        x = x * r
    else:
        pass
    #general score according to up - vote, need to work in way to make neut important...
    if x > 0:
        y = 1
    elif x == 0:
        y = 0
    else:
        y = -1
    #now if the obj is siginficant, i.e. been viewed extensively we take into account it's popularity
    #now calculate final score
    try:
        if x > 0:
            score = (3 * math.log(x + 1.0) + y) * dt
        else:
            score = -1
    except:
        score = 0
    return score


def calc_best(dt, spectrum, rating):
    #get spectrum list ex: [(-5,246), (-4,45), ... ,(5,121)]
    score = 0.0
    tot = 0.0
    for k, num in spectrum:
        score += k * num
        tot += num
    if tot != 0:
        score = score / tot
    return score


def get_ranked_list(parent, start, end, dimension, ctype_list, phase=None):

    if isinstance(start, int) and isinstance(end, int):
        try:
            start, end = (int(start), int(end))
        except:
            raise ValueError("The argument 'start=' and 'end=' to the pp_get_blob_list tag must be "
                                 "provided in the form of an int")
    else:
        try:
            start = int(start)
            end = int(end)
        except:
            raise ValueError(str(start) + ':' + str(type(start)) + '-' + str(end) + ':' + str(type(end)))

    tot_items = 0
    ctype = ContentType.objects.get_for_model(User)
    #c_type = ContentType.objects.get_for_model(m)
    #consensus_list = consensus_list.filter(content_type=c_type)
    if dimension:
        issue_list = Consensus.objects.all()
        if parent and isinstance(parent, Tag):
            issue_list = TaggedItem.objects.get_union_by_model(Consensus, parent)
        elif parent:
            #try to filter by topic
            pass
            issue_list = issue_list.filter(parent_pk=parent.pk)
        if ctype_list is not None:
            try:
                fd = ForumDimension.objects.get(key=ctype_list)
                type_class = ContentType.objects.get(app_label=str(fd.app_label), model=str(fd.model_class_name).lower())
                issue_list = issue_list.filter(content_type=type_class)
            except Exception, e:
                raise ValueError(str(ctype_list))
                #invalid ctype_list key
        if phase:
            issue_list = issue_list.filter(phasename=phase)
        issue_list = issue_list.exclude(content_type=ctype)
        #issue_list = Consensus.objects.all()
        tot_items = issue_list.count()
        next_issue_list = list(issue_list)

        if dimension == "n":
            order_by = '-submit_date'
            next_issue_list = issue_list.order_by(order_by)
            #next_issue_list = sorted(next_issue_list, key=lambda x: x.submit_date, reverse=True)
        elif dimension == "r":
            #must support random
            order_by = '-random'
            next_issue_list = issue_list.order_by(order_by)
        elif dimension == "x":
            #must support random
            order_by = '-consensus_percent'
            next_issue_list = issue_list.order_by('votes', order_by)
            #next_issue_list = sorted(next_issue_list, key=lambda x: x.submit_date, reverse=True)
        elif dimension == "h":
            order_by = '-interest'
            next_issue_list = issue_list.order_by(order_by)
            #next_issue_list = sorted(next_issue_list, key=lambda x: int(x.interest), reverse=True)
        elif dimension == "c":
            order_by = '-controversy'
            next_issue_list = issue_list.order_by(order_by)
            #next_issue_list = sorted(next_issue_list, key=lambda x: int(x.controversy), reverse=True)
        elif dimension == "t":
            order_by = 'votes'
            next_issue_list = issue_list.order_by(order_by)
        elif dimension == "b":
            order_by = '-best'
            next_issue_list = issue_list.order_by(order_by)
            #next_issue_list = sorted(next_issue_list, key=lambda x: int(x.votes), reverse=True)
        #elif dimension == "hn":
        #    dt = datetime.datetime.now()
        #    next_issue_list = sorted(next_issue_list, key=lambda x: (getattr(x, 'votes') * (96000.0 / (dt - (getattr(x, 'submit_date'))).seconds)) , reverse=True )
        else:
            raise ValueError("Illegal sorting dimension " + str(dimension))

        return_list = next_issue_list[int(start):int(end)]

    #else: #catch all for no dimension grabs new objects
    #    issue_lists = Consensus.objects.all().order_by('-submit_date')[int(start):int(end)]
    #   max_itr = 1

    #return_list = []
    #itr = 0
    #id_list = []
    #for i in range((end-start)):
    #    if itr >= max_itr: itr = 0
    #    try: iss=issue_lists[itr].pop()
    #    except: break
    #    if iss.id not in id_list:
    #        return_list.append(iss)
    #        id_list.append(iss.id)
    #    itr+=1

    #return_list.reverse()
    return return_list, tot_items


@task(ignore_result=True)
def update_rankings(sender, cons):

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
    except:
        pass
    #update the various ranking algorithms
    pis = cons.content_object
    spectrum = cons.spectrum.get_list()
    try:
        rating = cons.rating.get_list()
    except:
        #add rating to consensus if first rating
        rt = Rating()
        cons.rating = rt
        rt.save()
        rating = cons.rating.get_list()
    cons.save()
    dt = cons.submit_date
    timeDiff = (dt - datetime.datetime(2010, 7, 5, 20, 16, 19, 539498)).seconds
    timeNormFactor = (dt - datetime.datetime.now()).seconds

    dt = timeDiff / float(timeNormFactor)

    sols = [(('hot', calc_hot(dt, spectrum, rating)), ('cont', calc_controversial(dt, spectrum, rating)), ('best', calc_best(dt, spectrum, rating)))]

    ###I don't know why, but this fails if it's where it should be up above...
    from pirate_ranking.models import Ranking
    for scores in sols:
        for dim, sc in scores:
            try:
                obj = Ranking.objects.get(object_pk=pis.id, dimension=dim)
                obj.score = sc
                obj.save()
            except:
                contype = ContentType.objects.get_for_model(pis)
                newrank = Ranking(content_object=pis, dimension=dim, score=sc,
                            consensus_pk=cons.id, content_type=contype, object_pk=pis.id)
                newrank.save()
            if dim == 'hot':
                setattr(cons, 'interest', sc)
            if dim == 'cont':
                setattr(cons, 'controversy', sc)
            if dim == 'best':
                setattr(cons, 'best', sc)
            cons.save()
    ##Now we want to publish the vote event in the redis for nodejs to update
    print '*' * 50
    print 'publishing to: ' + str(cons.content_object.user.username)
    if sender != 'null':
        redis_client().publish(sender, json.dumps({'message': 'Someone voted on', 'object': str(cons.content_object.summary), 'type': 'vote', 'object_pk': str(cons.content_object.pk)}))

#When a vote is created via the consensus engine, this callback updates
#the issue ranked score, for each dimension
def vote_created_callback(sender, **kwargs):
    #udpate hot
    cons = kwargs.pop('parent', None)
    update_rankings.apply_async(args=[sender, cons])


vote_created.connect(vote_created_callback)
admin.site.register(Ranking)
