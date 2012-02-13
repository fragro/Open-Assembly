from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime
import django.dispatch
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from pirate_signals.models import vote_created
from djangotoolbox.fields import ListField



""" Spectrum and Rating classes hold denormalized
    counts for all votes/ratings so that the
    ranking algorithm requires only 3 DB hits rather
    than many.

    This could be accomplished in 1 DB hit by denormalizing these values into
    the consensus object, but then each value would unnecesarily
    be accessed each time consensus information is required.
"""


class SpectrumHolder(models.Model):
#mostly designed for chartit
    value = models.IntegerField(default=0)
    spectrum_pk = models.CharField(max_length=40)
    vote = models.CharField(max_length=5)

    def __unicode__(self):
        return str(self.value)
        #cons = Consensus.objects.get(spectrum=self)
        #return "%s:%s" % (str(cons.content_type), str(cons.object_pk))


class Spectrum(models.Model):
    #holds spectrum values for calculation of ranking, spectrum is not weighted
    spectrum1 = models.ForeignKey(SpectrumHolder, related_name="spectrum1", blank=True, null=True)
    spectrum2 = models.ForeignKey(SpectrumHolder, related_name="spectrum2", blank=True, null=True)
    spectrum3 = models.ForeignKey(SpectrumHolder, related_name="spectrum3", blank=True, null=True)
    spectrum4 = models.ForeignKey(SpectrumHolder, related_name="spectrum4", blank=True, null=True)
    spectrum5 = models.ForeignKey(SpectrumHolder, related_name="spectrum5", blank=True, null=True)
    spectrum6 = models.ForeignKey(SpectrumHolder, related_name="spectrum6", blank=True, null=True)
    spectrum7 = models.ForeignKey(SpectrumHolder, related_name="spectrum7", blank=True, null=True)
    spectrum8 = models.ForeignKey(SpectrumHolder, related_name="spectrum8", blank=True, null=True)
    spectrum9 = models.ForeignKey(SpectrumHolder, related_name="spectrum9", blank=True, null=True)
    spectrum10 = models.ForeignKey(SpectrumHolder, related_name="spectru10", blank=True, null=True)
    spectrum11 = models.ForeignKey(SpectrumHolder, related_name="spectrum11", blank=True, null=True)

    def __unicode__(self):
        return str(self.pk)
        #cons = Consensus.objects.get(spectrum=self)
        #return "%s:%s" % (str(cons.content_type), str(cons.object_pk))

    def save_vote(self, vote):
        spec = getattr(self, 'spectrum' + str(vote))
        try:
            spec.value += 1
            spec.save()
            setattr(self, 'spectrum' + str(vote), spec)
            self.save()
        except:
            specval = SpectrumHolder(value=1, spectrum_pk=self.pk, vote=str(vote))
            specval.save()
            setattr(self, 'spectrum' + str(vote), specval)
            self.save()

    def del_vote(self, vote):
        spec = getattr(self, 'spectrum' + str(vote))
        spec.value -= 1
        spec.save()
        setattr(self, 'spectrum' + str(vote), spec)
        self.save()

    def change_vote(self, vote, old_vote):
        self.del_vote(old_vote)
        self.save_vote(vote)

    def get_list(self):
        l = []
        for i in range(1, 12):
            sp = getattr(self, 'spectrum' + str(i))
            if sp is None:
                sp = SpectrumHolder(value=0, spectrum_pk=self.pk, vote=str(i))
                sp.save()
                setattr(self, 'spectrum' + str(i), sp)
                self.save()
                val = sp.value
            else:
                val = sp.value
            l.append((i - 6, val))
        return l


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

    def save_vote(self, vote):
        setattr(self, 'rating' + str(vote), getattr(self, 'rating' + str(vote)) + 1)
        #TODO: save rating_w and increment rating_n
        self.save()

    def del_vote(self, vote):
        setattr(self, 'rating' + str(vote), getattr(self, 'rating' + str(vote)) - 1)
        #TODO: save rating_w and increment rating_n
        self.save()

    def change_vote(self, vote, old_vote):
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
    phasename = models.CharField(max_length=30, blank=True, null=True)
    consensus_percent = models.FloatField(blank=True, null=True)
    reporting_percent = models.FloatField(blank=True, null=True)
    winners = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return str(self.content_type) + ' object:' + str(self.content_object) + ' self.pk:' + str(self.pk) + ' phase: ' + str(self.phasename)

    def register_vote(self, vote, dtype, old_vote=None):
        vtype = ContentType.objects.get_for_model(vote)
        uvote = ContentType.objects.get_for_model(UpDownVote)
        rvote = ContentType.objects.get_for_model(RatingVote)
        if vtype == uvote:
            if dtype == 'register':
                self.spectrum.save_vote(vote.vote)
            elif dtype == 'delete':
                self.spectrum.del_vote(vote.vote)
            elif dtype == 'change':
                self.spectrum.change_vote(vote.vote, old_vote)

        elif vtype == rvote:
            if dtype == 'register':
                self.rating.save_vote(vote.vote)
            elif dtype == 'delete':
                self.rating.del_vote(vote.vote)
            elif dtype == 'change':
                self.rating.change_vote(vote.vote, old_vote)
        else:
            raise ValueError('No matching vote type')

    def intiate_vote_distributions(self):
        spec = Spectrum()
        spec.save()
        self.spectrum = spec
        rate = Rating()
        rate.save()
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
    curphase = models.ForeignKey(PhaseLink)
    creation_dt = models.DateTimeField()
    decision_dt = models.DateTimeField()
    phase_change_dt = models.DateTimeField()
    complete = models.BooleanField()
    active = models.BooleanField()

    def __unicode__(self):
        return str(self.curphase.phasename)


#This is the basic voting object utilized with Reddit-like consensus
class UpDownVote(models.Model):
    # Content-object field
    parent = models.ForeignKey(Consensus,
            verbose_name=_('parent'))
    parent_pk = models.CharField(max_length=100, blank=True, null=True)
    submit_date = models.DateTimeField(_('date/time submitted'), default=None)
    user = models.ForeignKey(User, verbose_name=_('user'),
                    blank=True, null=True, related_name="%(class)s_ratings")
    vote = models.IntegerField()
    object_pk = models.CharField(_('Object_PK'), max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _('Up/Down Vote')
        verbose_name_plural = _('Up/Down Votes')

    def __unicode__(self):
        return " on %s" % (self.parent.content_object)

    def save(self, *args, **kwargs):
        if self.submit_date is None:
            self.submit_date = datetime.datetime.now()
            self.parent.votes += 1
            self.parent.save()
            #update consensus object vote count
        super(UpDownVote, self).save(*args, **kwargs)


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
    parent = models.ForeignKey(Consensus,
            verbose_name=_('parent'), related_name=_('parent'))
    user = models.ForeignKey(User, verbose_name=_('user'),
                    blank=True, null=True, related_name="%(class)s_ratings")
    ranked_vote = models.IntegerField(blank=True, null=True)
    nom_cons = models.ForeignKey(Consensus,
                    verbose_name=_('nomination consensus'), related_name=_('nomination consensus'), blank=True, null=True)

    class Meta:
        verbose_name = _('ranked vote')
        verbose_name_plural = _('ranked votes')

    def __unicode__(self):
        return "%s : %s" % (self.user, self.parent)


class ConfirmRankedVote(models.Model):
    confirm = models.BooleanField()
    parent = models.ForeignKey(Consensus,
            verbose_name=_('parent'), related_name=_('confirm_parent'))
    user = models.ForeignKey(User, verbose_name=_('user'),
                    blank=True, null=True, related_name="confirm_%(class)s_ratings")
    submit_date = models.DateTimeField(_('date/time submitted'), default=None, blank=True, null=True)

    def __unicode__(self):
        return str(self.id)
        #cons = Consensus.objects.get(rating=self)
        #return "%s:%s" % (str(cons.content_type), str(cons.object_pk))


class RankedDecision(models.Model):
    parent = models.ForeignKey(Consensus,
            verbose_name=_('parent'), related_name=_('decision_parent'))
    algorithm = models.CharField(max_length=100)
    submit_date = models.DateTimeField(_('date/time submitted'), default=None, blank=True, null=True)
    winner = ListField()
    passed = models.BooleanField()
    consensus_percent = models.FloatField()
    reporting_percent = models.FloatField()

    def __unicode__(self):
        return str(self.id)
        #cons = Consensus.objects.get(rating=self)
        #return "%s:%s" % (str(cons.content_type), str(cons.object_pk))


class WeightedVote(models.Model):
    """Facilitates all classes of weighted voting algorithms
        All weights must add up to max. Otherwise vote is not valid.
    """
    parent = models.ForeignKey(Consensus,
            verbose_name=_('parent'))
    submit_date = models.DateTimeField(_('date/time submitted'), default=None)
    user = models.ForeignKey(User, verbose_name=_('user'),
                    blank=True, null=True, related_name="%(class)s_ratings")
    vote_weight = models.FloatField()
    #should add up to 1

    class Meta:
        unique_together = (('parent', 'user'),)
        verbose_name = _('weighted vote')
        verbose_name_plural = _('weighted votes')

    def __unicode__(self):
        return "%s: %s" % (self.user, self.vote_weight)

    def save(self, force_insert=False, force_update=False):
        if self.submit_date is None:
            self.submit_date = datetime.datetime.now()
            self.parent.votes += 1
            #update consensus object vote count
            self.parent.save()
        super(UpDownVote, self).save(force_insert, force_update)


class RatingVote(models.Model):
    """
    Star Vote used for ranking items in a range from [0:N] where N is the number
    of stars specified via the ajax/javascript star rating functionality.
    """
    parent = models.ForeignKey(Consensus,
            verbose_name=_('parent'))
    parent_pk = models.CharField(max_length=100, blank=True, null=True)
    submit_date = models.DateTimeField(_('date/time submitted'), default=None)
    user = models.ForeignKey(User, verbose_name=_('user'),
                    blank=True, null=True, related_name="%(class)s_ratings")
    vote = models.IntegerField()
    #should add up to 1
    object_pk = models.CharField(_('Object_PK'), max_length=100)

    class Meta:
        verbose_name = _('star rating')
        verbose_name_plural = _('star ratings')

    def __unicode__(self):
        return " on %s" % (self.parent.content_object)

    def save(self, *args, **kwargs):
        if self.submit_date is None:
            self.submit_date = datetime.datetime.now()
            self.parent.ratings += 1
            #update consensus object vote count
            self.parent.save()
        super(RatingVote, self).save(*args, **kwargs)


###SIGNALS
admin.site.register(Consensus)
admin.site.register(UpDownVote)
admin.site.register(VideoVote)
admin.site.register(RankedVote)
admin.site.register(ConfirmRankedVote)
admin.site.register(WeightedVote)
admin.site.register(RatingVote)
admin.site.register(Spectrum)
admin.site.register(Rating)
admin.site.register(Phase)
admin.site.register(PhaseLink)
admin.site.register(RankedDecision)
