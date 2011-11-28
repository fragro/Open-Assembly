from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from djangotoolbox.fields import ListField
from django.utils.translation import ugettext as _
from django.contrib import admin
from pirate_signals.models import update_agent
from google.appengine.ext import deferred
from settings import OPENASSEMBLY_AGENT, DOMAIN_NAME, OPENASSEMBLY_KEY
from Proxy import Proxy
from django.contrib.contenttypes import generic


class PlatformDimension(models.Model):
    initiator = models.ForeignKey(User, blank=True, null=True)
    created_dt = models.DateTimeField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType,
                verbose_name=('content type'),
                related_name="content_type_set_for_forumdimension_of_platform_for_%(class)s")
    num_planks = models.IntegerField()
    deadline_dt = models.DateTimeField(null=True, blank=True)
    vote_deadline_dt = models.DateTimeField(null=True, blank=True)
    content_type_obj = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_platform_dim_for_%(class)s", null=True, blank=True)
    object_pk = models.IntegerField(_('object ID'), null=True, blank=True)
    content_object = generic.GenericForeignKey(ct_field="content_type_obj", fk_field="object_pk")
    complete = models.BooleanField(default=False)

    def __unicode__(self):
        return self.content_type.name

    def get_absolute_url(self):
        return '/index.html#platform' + '/_t' + str(self.content_type_obj.pk) + '/_o' + str(self.object_pk)


class Platform(models.Model):
    """This platform model contains a list of ids and a model type
        for each user"""
    dimension = models.ForeignKey(PlatformDimension, null=True, blank=True)
    user = models.ForeignKey(User,
            verbose_name=_('user'), blank=True,
            null=True, related_name="%(class)s_ratings")
    planks = ListField(models.IntegerField())
    content_type = models.ForeignKey(ContentType,
                verbose_name=('content type'),
                related_name="content_type_set_for_%(class)s")

    def __unicode__(self):
        return str(self.user.username) + ': ' + str(self.content_type.name)


def deferupdate(updatetype, params):
    #p = Proxy(OPENASSEMBLY_AGENT)
    #p.update(DOMAIN_NAME, OPENASSEMBLY_KEY, updatetype,
    #                                            params)
    #don't update till we have the agent online
    pass


def update(**kwargs):
    #update_agent.send(sender=obj, type="content",
    #                       params=["pirate_issues", "problem", obj.pk])
    #["http://localhost:8000","frank", "content",
    #                       ["pirate_issues","problem","12345946"]
    updatetype = kwargs.get('type', None)
    params = kwargs.get('params', None)
    deferred.defer(deferupdate, updatetype, params, _countdown=60)

update_agent.connect(update)

admin.site.register(Platform)
admin.site.register(PlatformDimension)

# Create your models here.
