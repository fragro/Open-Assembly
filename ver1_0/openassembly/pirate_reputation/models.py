from exceptions import ImportError, ValueError
from django.contrib import admin
from django.db import models
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime
from djangotoolbox import fields

from pirate_consensus.models import Consensus, Spectrum, Rating

from pirate_signals.models import aso_rep_event,aso_rep_delete, aso_rep_change

#event_registered = Signal(providing_args=["","",""])


class ReputationManager(models.Manager):

    def transitive_vote(self, vote, user, dtype, old_vote=None):
        """
        When a vote is registered in the reputation system, the vote type
        is normalized into a Consensus object stored for each user, allowing
        ease in accessing distributions of other user's votes for this user.
        """

        contype = ContentType.objects.get_for_model(user)
        cons, is_new = Consensus.objects.get_or_create(content_type=contype,
                                    object_pk=user.pk,
                                    vote_type=contype,
                                    parent_pk=user.pk)
        if is_new:
            cons.intiate_vote_distributions()
        cons.register_vote(vote, dtype)
        cons.save()

    def register_event(self, event_score, user, dimension=None,
                       related_object=None, initiator=None,
                       calculator=(lambda x, user, related_obj, initiator, dimension: x),
                       aggregator=(lambda x, user, related_obj, initiator, aggregation: x)):
        '''
        When an event is registered, it is possible to supply function callbacks that are used
        to calculate the improvment in the single-dimension score (i.e. calculator), as well
        as to calculate the improvement in the aggregate score (i.e. aggregator).

        If neither of these are specified, which is the usual case, then the event_score is
        simply used without alteration.
        '''
        if dimension == None:
            dimension = ReputationDimension.objects.null_dimension()
        reputations = self.filter(user=user, dimension=dimension)

        ## TODO: DJANGO-NONREL BUG
        ## Maybe this isn't supposed to work (although gae does have count(), limited to 1000)
        #reputation_count = reputations.count()
        ## But for some reason this doesn't work either, although it should...
        #reputation_count = len(reputations)
        ## And yet this does work...
        reputation_count = len(reputations)

        if reputation_count == 1:
            reputation = reputations[0]
            aggregation = reputation.aggregation

            # Just make sure that the aggregation was assigned properly...
            try:
                assert aggregation.user == user and aggregation.dimension == None
            except:
                aggreg_delta = 0
                         #TODO:for some reason the aggregation exists in the admin panel, but
                         #here aggregation == None

        elif reputation_count == 0:
            #aggregations are disabled until we can find a better way to use ite
            aggregation = None

            #aggregations = self.filter(user=user, dimension=None, aggregation=None)
            #aggregation_count = len(list(aggregations))

            #if aggregation_count == 1:
            #    aggregation = aggregations[0]
            #elif aggregation_count == 0:
            #    aggregation = self.model(user=user, dimension=None)
            #else:
            #    raise ValueError("More than one aggregating reputation found for user.")

            reputation = self.model(user=user, dimension=dimension, aggregation=aggregation)
        else:
            raise ValueError("More than one reputation found for user and dimension.")

        ## Calculate the score delta, and then assign it
        score_delta = calculator(event_score, user, related_object, initiator, dimension)
        reputation.score += score_delta
        reputation.save()

        ## Same for aggregation, if there is one
        if aggregation is not None:
            aggreg_delta = aggregator(event_score, user, related_object,
                                      initiator, aggregation)
            aggregation.score += aggreg_delta
            aggregation.save()
        else:
            aggreg_delta = None

        initiator = user if initiator is None else initiator

        if related_object is not None:
            obj_id = related_object.pk
            content_type = ContentType.objects.get_for_model(related_object)
        else:
            obj_id = None
            content_type = None

        reputation_event = ReputationEvent(user=user, score=reputation,
                                           score_delta=score_delta, aggregation=aggregation,
                                           aggregation_delta=aggreg_delta,
                                           dimension=dimension, initiator=initiator,
                                           object_id=obj_id, content_type=content_type)
                                           #related_object=related_object)
        reputation_event.save()

    def get_user_score(self, user, dimension=None):
        if dimension == None:
            dimension = ReputationDimension.objects.null_dimension()

        ## TODO
        reputations = self.filter(user=user, dimension=dimension)
        reputation_count = len(list(reputations))
        if reputation_count == 1:
            return reputations[0]
        elif reputation_count == 0:
            return None
        else:
            raise ValueError("More than one reputation found for user and aspect.")


class DimensionManager(models.Manager):
    def null_dimension(self):
        return self.get_or_create(name=None)[0]

    def get(self, name=None):
        return self.get_or_create(name=name)[0]


class AbuseTicket(models.Model):

    user = models.ForeignKey(User)
    name_of_abuser = models.CharField(max_length=70, unique=True)
    created_dt = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=800, null=True, blank=True)
    description_of_abuse = models.CharField(max_length=500)
    fixed = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.name_of_abuser) + ' - ' + str(self.created_dt)


class FeedbackTicket(models.Model):

    user = models.ForeignKey(User)
    feedback = models.CharField(max_length=500)
    created_dt = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.user.username) + ' - ' + str(self.created_dt)


class ReputationDimension(models.Model):
    name = models.CharField(max_length=70, null=True, unique=True)
    created_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now=True)

    objects = DimensionManager()

    def __unicode__(self):
        return self.name


class Reputation(models.Model):

    user = models.ForeignKey(User)
    score = models.IntegerField(default=0)

    # dimension and aggregation are None if the ReputationScore itself is an aggregation
    dimension = models.ForeignKey(ReputationDimension, null=True)
    aggregation = models.ForeignKey('self', null=True)

    created_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now=True)

    objects = ReputationManager()

    def __str__(self):
        return "<Reputation: user=%s, score=%s, dimension=%s>" % \
                                       (self.user, self.score, self.dimension)

    class Meta:
        unique_together = ("user", "dimension")


class ReputationEvent(models.Model):

    user = models.ForeignKey(User)
    initiator = models.ForeignKey(User, related_name="initiated_event_set")

    score = models.ForeignKey(Reputation)
    score_delta = models.IntegerField()
    aggregation = models.ForeignKey(Reputation, related_name="aggregated_event_set", null=True)
    aggregation_delta = models.IntegerField(null=True)

    dimension = models.CharField(max_length=70, null=True, blank=True)
    related_object = generic.GenericForeignKey('content_type', 'object_id')

    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.CharField(max_length=100, blank=True, null=True)

    created_dt = models.DateTimeField(auto_now_add=True)

    def save(self):
        if not self.id:
            return super(ReputationEvent, self).save()
        raise SuspiciousOperation("A ReputationEvent cannot be modified after it is created.")

    def __unicode__(self):
        return str(self.user) + '-' + str(self.dimension) + '-' + str(self.created_dt) + '-' + str(self.object_id)

    def get_absolute_url(self):
        try:
            return self.related_object.get_absolute_url()
        except:
            try:
                return self.related_object.content_object.get_absolute_url()
            except:
                return "/"
                #this should only occur for the old ReputationEvents that are malformed

admin.site.register(Reputation)
admin.site.register(ReputationEvent)
admin.site.register(ReputationDimension)
admin.site.register(AbuseTicket)

###Cannot import from pirate_reputation.models from pirate_reputation.callbacks?

#This callback takes the signal of a reputation event and
#calls a register_event, taking care of the calculator
#and aggregator functions


def register_reputation_event(event_score, user, **kwargs):
    #first check **kwargs for non-mandatory arguments
    dimension = kwargs.get('dimension',  None)
    initiator = kwargs.get('initiator', None)
    related_object = kwargs.get('related_object', None)

    is_vote = kwargs.get('is_vote', False)
    if is_vote:
        Reputation.objects.transitive_vote(related_object, user, 'register')

    Reputation.objects.register_event(event_score, user, dimension, initiator=initiator, related_object=related_object)


def delete_reputation_event(event_score, user, **kwargs):
    #first check **kwargs for non-mandatory arguments
    dimension = kwargs.get('dimension', None)
    initiator = kwargs.get('initiator', None)
    related_object = kwargs.get('related_object', None)
    obj_id = related_object.pk
    content_type = ContentType.objects.get_for_model(related_object)

    is_vote = kwargs.get('is_vote', False)
    if is_vote:
        Reputation.objects.transitive_vote(related_object, user, 'delete')

    try:
        rep = ReputationEvent.objects.get(user=user, dimension=dimension, initiator=initiator, object_id=obj_id,
                                        content_type=content_type)
        rep.delete()
        rep_obj = Reputation.objects.get(user=user, dimension=dimension)
        rep_obj.score -= event_score
        rep_obj.save()
    except:
        pass
        #maybe this event never even existed in the case of error


#primarily used to adjust votes for transitive purposes
def change_reputation_event(event_score, user, **kwargs):
    #first check **kwargs for non-mandatory arguments
    dimension= kwargs.get('dimension', None)
    initiator=kwargs.get('initiator', None)
    related_object = kwargs.get('related_object', None)
    obj_id = related_object.pk
    content_type = ContentType.objects.get_for_model(related_object)

    is_vote = kwargs.get('is_vote', False)
    old_vote = kwargs.get('old_vote', False)
    if is_vote:
        Reputation.objects.transitive_vote(related_object, user,'change',old_vote)



####SIGNAL RELATED
aso_rep_change.connect(change_reputation_event)  
aso_rep_event.connect(register_reputation_event)  
aso_rep_delete.connect(delete_reputation_event)    
