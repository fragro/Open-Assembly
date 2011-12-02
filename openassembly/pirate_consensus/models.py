from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime
import django.dispatch
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from pirate_signals.models import vote_created


""" Spectrum and Rating classes hold denormalized
    counts for all votes/ratings so that the
    ranking algorithm requires only 3 DB hits rather
    than many.

    This could be accomplished in 1 DB hit by denormalizing these values into
    the consensus object, but then each value would unnecesarily
    be accessed each time consensus information is required.
"""


class Spectrum(models.Model):
    #holds spectrum values for calculation of ranking, spectrum is not weighted
    spectrum1 = models.IntegerField(default=0)
    spectrum2 = models.IntegerField(default=0)
    spectrum3 = models.IntegerField(default=0)
    spectrum4 = models.IntegerField(default=0)
    spectrum5 = models.IntegerField(default=0)
    spectrum6 = models.IntegerField(default=0)
    spectrum7 = models.IntegerField(default=0)
    spectrum8 = models.IntegerField(default=0)
    spectrum9 = models.IntegerField(default=0)
    spectrum10 = models.IntegerField(default=0)
    spectrum11 = models.IntegerField(default=0)
    
    def __unicode__(self):
        return str(self.id)
        #cons = Consensus.objects.get(spectrum=self)
        #return "%s:%s" % (str(cons.content_type), str(cons.object_pk))
    
    def save_vote(self, vote):
        setattr(self, 'spectrum' + str(vote), getattr(self,'spectrum' + str(vote))+1)
        self.save()

    def del_vote(self,vote):
        setattr(self, 'spectrum' + str(vote), getattr(self,'spectrum' + str(vote))-1)
        #TODO: save rating_w and increment rating_n
        self.save()
        
    def change_vote(self,vote,old_vote):
        setattr(self, 'spectrum' + str(old_vote), getattr(self,'spectrum' + str(old_vote))-1)
        setattr(self, 'spectrum' + str(vote), getattr(self,'spectrum' + str(vote))+1)
        #TODO: save rating_w and increment rating_n
        self.save()
        
    def get_list(self):
        return [(i-6, getattr(self,'spectrum' + str(i))) for i in range(1,12)]
    
class Rating(models.Model):
    #ratings
    rating1 = models.IntegerField(default=0)
    rating2 = models.IntegerField(default=0)
    rating3 = models.IntegerField(default=0)
    rating4 = models.IntegerField(default=0)
    rating5 = models.IntegerField(default=0)
    
    #average weights based on rating reputation of rating users
    rating_w1 = models.FloatField(default=0.0)
    rating_w2 = models.FloatField(default=0.0)
    rating_w3 = models.FloatField(default=0.0)
    rating_w4 = models.FloatField(default=0.0)
    rating_w5 = models.FloatField(default=0.0)
    
    def __unicode__(self):
        return str(self.id)
        #cons = Consensus.objects.get(rating=self)
        #return "%s:%s" % (str(cons.content_type), str(cons.object_pk))
    
    def save_vote(self,vote):
        setattr(self, 'rating' + str(vote), getattr(self, 'rating' + str(vote)) + 1)
        #TODO: save rating_w and increment rating_n
        self.save()
        
    def del_vote(self,vote):
        setattr(self, 'rating' + str(vote), getattr(self, 'rating' + str(vote)) - 1)
        #TODO: save rating_w and increment rating_n
        self.save()

    def change_vote(self,vote,old_vote):
        setattr(self, 'rating' + str(old_vote), getattr(self, 'rating' + str(old_vote)) - 1)
        setattr(self, 'rating' + str(vote), getattr(self, 'rating' + str(vote)) + 1)
        #TODO: save rating_w and increment rating_n
        self.save()

    def get_list(self):
        #TODO: Implement weighted voting on ratings
        #w = getattr(self,'rating_w' + str(i))/getattr(self,'rating_n' + str(i))
        w = 1.0
        return [(i, w, getattr(self, 'rating' + str(i))) for i in range(1, 6)]


class Consensus(models.Model):
    #Generic conesensus object that acts as parent for all agree/disagree/votes

    parent_pk = models.CharField(max_length=40, blank=True, null=True)
    submit_date = models.DateTimeField(_('date/time submitted'), auto_now_add=True)
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_set_for_%(class)s")
    object_pk = models.CharField(_('object ID'), max_length=100)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    #number of children
    votes = models.IntegerField(default=0)
    ratings = models.IntegerField(default=0)
    #denormalized ranking values
    interest = models.FloatField(default=0.0)
    controversy = models.FloatField(default=0.0)
    is_edittable = models.BooleanField(default=True)
    #refers to edittable property of parent, nullified by a vote

    #related to children vote types, to allow for ranked/weighted voting
    vote_type = models.ForeignKey(ContentType,
                                      verbose_name=_('vote content type'),
                                      related_name="vote_content_type_set_for_%(class)s", blank=True, null=True)
    child_vote_type = models.ForeignKey(ContentType,
                                      verbose_name=_('child vote content type'),
                                      related_name="child_vote_content_type_set_for_%(class)s", blank=True, null=True)
    spectrum = models.ForeignKey(Spectrum, verbose_name=_('spectrum votes'), null=True)
    rating = models.ForeignKey(Rating, verbose_name=_('rating votes'), null=True)
    vote_rate = models.FloatField(default=0.0, null=None, blank=None)
    phase = models.ForeignKey("Phase", blank=True, null=True, related_name="consensus_phase")

    def __unicode__(self):
        return str(self.content_type) + ' object:' + str(self.object_pk) + ' self.pk:' + str(self.pk)

    def register_vote(self, vote, dtype, old_vote=None):
        vtype = ContentType.objects.get_for_model(vote)
        uvote = ContentType.objects.get_for_model(UpDownVote)
        rvote = ContentType.objects.get_for_model(RatingVote)
        if vtype == uvote:
            if self.spectrum == None:
                sp = Spectrum()
                self.spectrum = sp
                sp.save()
                self.save()
            if dtype == 'register':
                self.spectrum.save_vote(vote.vote_type)
            elif dtype == 'delete':
                self.spectrum.del_vote(vote.vote_type)
            elif dtype == 'change':
                self.spectrum.change_vote(vote.vote_type, old_vote)

        elif vtype == rvote:
            if self.rating == None:
                rt = Rating()
                self.rating = rt
                rt.save()
                self.save()
            if dtype == 'register':
                self.rating.save_vote(vote.vote_pos)
            elif dtype == 'delete':
                self.rating.del_vote(vote.vote_pos)
            elif dtype == 'change':
                self.rating.change_vote(vote.vote_pos, old_vote)

    def intiate_vote_distributions(self):
        spec = Spectrum()
        rate = Rating()
        spec.save()
        rate.save()
        self.spectrum = spec
        self.rating = rate
        self.save()


class PhaseLink(models.Model):
    prevphase = models.ForeignKey("PhaseLink", blank=True, null=True, related_name="phase prevphase")
    phasename = models.CharField(max_length=100)
    verb = models.CharField(max_length=100)
    nextphase = models.ForeignKey("PhaseLink", blank=True, null=True, related_name="phase nextphase")

    def __unicode__(self):
        return str(self.phasename)


class Phase(models.Model):
    """
    Handles the phases of voting, saves the necessary time information
    """
    consensus = models.ForeignKey(Consensus, related_name="consensus of phase")
    curphase = models.ForeignKey(PhaseLink)
    creation_dt = models.DateTimeField()
    decision_dt = models.DateTimeField()
    phase_change_dt = models.DateTimeField()
    complete = models.BooleanField()
    active = models.BooleanField()

    def __unicode__(self):
        return str(self.consensus) + " " + str(self.complete)


#This is the basic voting object utilized with Reddit-like consensus
class UpDownVote(models.Model):
    # Content-object field
    parent = models.ForeignKey(Consensus,
            verbose_name=_('parent'))
    parent_pk = models.CharField(max_length=100, blank=True, null=True)
    submit_date = models.DateTimeField(_('date/time submitted'), default=None)
    user = models.ForeignKey(User, verbose_name=_('user'),
                    blank=True, null=True, related_name="%(class)s_ratings")
    vote_type = models.IntegerField()
    #For simplicity upvote == 1, downvote == -1, neut == 0
    object_pk = models.CharField(_('Object_PK'), max_length=100, blank=True, null=True)

    class Meta:
        unique_together = (('parent', 'user'),)
        verbose_name = _('Up/Down Vote')
        verbose_name_plural = _('Up/Down Votes')

    def __unicode__(self):
        return " on %s" % (self.parent.content_object)

    def save(self, force_insert=False, force_update=False):
        if self.submit_date is None:
            self.submit_date = datetime.datetime.now()
            self.parent.votes += 1
            #update consensus object vote count
        super(UpDownVote, self).save(force_insert, force_update)

        spec = self.parent.spectrum
        if spec != None:
            spec.save_vote(self.vote_type)
        else:
            spec = Spectrum()
            spec.save()

            self.parent.spectrum = spec
            spec.save_vote(self.vote_type)

        self.parent.save()


class VideoVote(models.Model):
    """
    Integrates OpenAssembly with HTML5 video voting, allowing users 
    to easily vote on the scenes they like in videos. Stores info 
    such as video ID and time in the video voted.
    """
    user = models.ForeignKey(User, null=True, blank=True)
    submit_date = models.DateTimeField(_('date/time submitted'), auto_now_add=True)
    video_id = models.IntegerField()
    time = models.FloatField()
    duration = models.FloatField()
    
    
    def __unicode__(self):
        return "user:%s - video_id:%s - time:%s" % (self.user, self.video_id, self.time)
        

class RankedVote(models.Model):
    """Facilitates ranked voting methods such as the Schulz voting algorithm.
        The correctness of the ranking can be checked via the template tags,
        or via the javascript interface. Incorrect rankings should not be allowed.
    """
    parent   = models.ForeignKey(Consensus,
            verbose_name=_('parent'))
    submit_date = models.DateTimeField(_('date/time submitted'), default=None)
    user        = models.ForeignKey(User, verbose_name=_('user'),
                    blank=True, null=True, related_name="%(class)s_ratings")
    vote_rank = models.IntegerField() 
    
    class Meta:
        unique_together = (('parent', 'user'),)
        verbose_name = _('ranked vote')
        verbose_name_plural = _('ranked votes')
    
    def __unicode__(self):
        return "%s: %s" % (self.user, self.vote_rank)
    
    def save(self, force_insert=False, force_update=False):
        if self.submit_date is None:
            self.submit_date = datetime.datetime.now()
        super(UpDownVote, self).save(force_insert, force_update)
        self.parent.votes += 1 #update consensus object vote count
        self.parent.save()
        
class WeightedVote(models.Model):
    """Facilitates all classes of weighted voting algorithms
        All weights must add up to max. Otherwise vote is not valid.
    """
    parent   = models.ForeignKey(Consensus,
            verbose_name=_('parent'))
    submit_date = models.DateTimeField(_('date/time submitted'), default=None)
    user        = models.ForeignKey(User, verbose_name=_('user'),
                    blank=True, null=True, related_name="%(class)s_ratings")
    vote_weight = models.FloatField() #should add up to 1
    
    class Meta:
        unique_together = (('parent', 'user'),)
        verbose_name = _('weighted vote')
        verbose_name_plural = _('weighted votes')
    
    def __unicode__(self):
        return "%s: %s" % (self.user, self.vote_weight)
    
    def save(self, force_insert=False, force_update=False):
        if self.submit_date is None:
            self.submit_date = datetime.datetime.now()
        super(UpDownVote, self).save(force_insert, force_update)
        self.parent.votes += 1 #update consensus object vote count
        self.parent.save()

class RatingVote(models.Model):
    """
    Star Vote used for ranking items in a range from [0:N] where N is the number 
    of stars specified via the ajax/javascript star rating functionality.
    """
    parent   = models.ForeignKey(Consensus,
            verbose_name=_('parent'))
    parent_pk = models.CharField(max_length=100, blank=True, null=True)
    submit_date = models.DateTimeField(_('date/time submitted'), default=None)
    user        = models.ForeignKey(User, verbose_name=_('user'),
                    blank=True, null=True, related_name="%(class)s_ratings")
    vote_pos = models.IntegerField() #should add up to 1
    object_pk = models.CharField(_('Object_PK'), max_length=100)
    
    class Meta:
        unique_together = (('object_pk', 'user'),)
        verbose_name = _('star rating')
        verbose_name_plural = _('star ratings')
    
    def __unicode__(self):
        return " on %s" % (self.parent.content_object)
    
    def save(self, force_insert=False, force_update=False):
        if self.submit_date is None:
            self.submit_date = datetime.datetime.now()
        super(RatingVote, self).save(force_insert, force_update)
        self.parent.ratings += 1 #update consensus object vote count
        rate = self.parent.rating
        if rate != None:
            rate.save_vote(self.vote_pos)
        else:
            rating = Rating()
            rating.save()
            self.parent.rating = rating
        
        self.parent.save()
    
        
###SIGNALS
admin.site.register(Consensus)
admin.site.register(UpDownVote)
admin.site.register(VideoVote)
admin.site.register(RankedVote)
admin.site.register(WeightedVote)
admin.site.register(RatingVote)
admin.site.register(Spectrum)
admin.site.register(Rating)
admin.site.register(Phase)
admin.site.register(PhaseLink)
