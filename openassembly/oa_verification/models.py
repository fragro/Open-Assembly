from django.db import models
from django import template
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.comments.signals import comment_was_posted
from pirate_permissions.models import Permission
from pirate_sources.models import IMGSource
from django.utils.translation import ugettext as _
from pirate_topics.models import Topic


class ActionTaken(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_set_for_%(class)s")
    object_pk = models.CharField(_('object ID'), max_length=100)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    url = models.CharField(max_length=200, blank=True, null=True)
    verb = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return str(self.user.username) + " - " + str(self.content_type) + " : " + str(self.object_pk)


class Referral(models.Model):
    user = models.ForeignKey(User, related_name="referral_submission_user")
    referred_user = models.ForeignKey(User, blank=True, null=True, related_name="referred_user")
    created_dt = models.DateTimeField()
    accepted_dt = models.DateTimeField(blank=True, null=True)
    key = models.CharField(max_length=250)
    accepted = models.BooleanField()
    email = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, blank=True, null=True)

    def __unicode__(self):
        return '{%s : %s}' % (self.user.username, self.topic.shortname)


class EmailVerification(models.Model):
    user = models.ForeignKey(User)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()


class arpv(models.Model):
    photo = models.ForeignKey(IMGSource)
    submit_user = models.ForeignKey(User, related_name="submit_user")
    user1 = models.ForeignKey(User, related_name="user1")
    user2 = models.ForeignKey(User, related_name="user2")
    user1Confirm = models.BooleanField(default=False)
    user2Confirm = models.BooleanField(default=False)
    verifications = models.IntegerField(default=0)
    created_dt = models.DateTimeField()

    def __unicode__(self):
        return '{%s : %s}' % (self.user1, self.user2)

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = "arpv_confirm.html?_t=" + str(content_type.pk) + "&_o=" + str(self.pk)
        return path


class PhotoVerificationTask(models.Model):
    pv1 = models.ForeignKey(arpv, related_name="photo_verification1")
    pv2 = models.ForeignKey(arpv, related_name="photo_verification2")
    user1 = models.ForeignKey(User, related_name="task_user1")
    user2 = models.ForeignKey(User, related_name="task_user2")
    user3 = models.ForeignKey(User, related_name="task_user3")
    user4 = models.ForeignKey(User, related_name="task_user4")
    created_dt = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(User, blank=True, null=True)
    verified_dt = models.DateTimeField(blank=True, null=True)
    verification = models.BooleanField(default=False)
    #if this is a verified photo or illegal
    complete = models.BooleanField(default=False)
    #once this task has been completed

    def __unicode__(self):
        return '{%s : %s : %s}' % (self.pv1.pk, self.pv2.pk, self.complete)


class PhotoUserVerifications(models.Model):
    user = models.ForeignKey(User)
    verifications = models.IntegerField(default=0)

    def __unicode__(self):
        return '%s : %s' % (self.user.username, self.verifications)


admin.site.register(ActionTaken)
admin.site.register(EmailVerification)
admin.site.register(arpv)
admin.site.register(Referral)
admin.site.register(PhotoVerificationTask)
admin.site.register(PhotoUserVerifications)
