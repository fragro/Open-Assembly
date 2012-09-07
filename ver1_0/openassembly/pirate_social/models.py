from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
import datetime
import django.dispatch
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
from pirate_signals.models import relationship_event, delete_relationship_event

"""
Social module contains all references to the real world, social networks,
locations, photo verification systems, etc.
"""

"""
Locations can correspond to users, forum_blobs, or other objects.
"""


class Location(models.Model):
    city = models.TextField(max_length=500, null=True, blank=True)
    state = models.TextField(max_length=500, null=True, blank=True)
    country = models.TextField(max_length=500, null=True, blank=True)
    object_pk = models.CharField(_('object ID'), max_length=100)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_set_for_%(class)s")


class Address(models.Model):
    address = models.CharField(max_length=500)
    zipcode = models.TextField(max_length=10)


class Subscription(models.Model):
    subscriber = models.ForeignKey(User, verbose_name=_('subscriber'), related_name=_('subscriber'))
    subscribee = models.ForeignKey(User, verbose_name=_('subscribee'), related_name=_('subscribee'))
    created_dt = models.DateTimeField(_('date/time subscription created'), auto_now_add=True)

    def __str__(self):
        return str(self.subscriber.username) + ":" + str(self.subscribee.username)


class RelationshipEvent(models.Model):
    initiator = models.ForeignKey(User, verbose_name=_('initiator user'), related_name=_('initiator'))
    target = models.ForeignKey(User, verbose_name=_('target user'), related_name=_('target'), blank=True, null=True)
    created_on = models.DateTimeField(_('date/time occured'), auto_now_add=True)
    ini_content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('initiator content type'),
                                      related_name="ini_content_type_set_for_%(class)s")
    ini_object_pk = models.CharField(_('initiator object ID'), max_length=100)
    ini_content_object = generic.GenericForeignKey(ct_field="ini_content_type", fk_field="ini_object_pk")
    tar_content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('target content type'),
                                      related_name="tar_content_type_set_for_%(class)s")
    tar_object_pk = models.CharField(_('target object ID'), max_length=100)
    tar_content_object = generic.GenericForeignKey(ct_field="tar_content_type", fk_field="tar_object_pk")

    class Meta:
        # Enforce unique tag association per object
        verbose_name = _('relationship event')
        verbose_name_plural = _('relationship events')
        unique_together = (('initiator', 'ini_object_pk', 'tar_object_pk'),)

    def __str__(self):
        return u'[%s:%s]' % (self.initiator.username, self.created_on)

    def get_ini_type(self):
        return str(self.ini_content_type)


def register_relationship_event(obj, parent, **kwargs):
        ini_c_type = ContentType.objects.get_for_model(obj)
        if parent != None:
            parent_c_type = ContentType.objects.get_for_model(parent)
        initiator = kwargs.get('initiator', None)
        if initiator == None:
            try:
                initiator = obj.user
            except:
                pass
        if parent != None:
            try:
                target_user = parent.user
            except:
                target_user = None

            rel = RelationshipEvent(initiator=initiator, 
                                ini_object_pk=obj.pk,
                                ini_content_type=ini_c_type, 
                                tar_object_pk=parent.pk,
                                tar_content_type=parent_c_type,
                                target=target_user)
        else: rel = RelationshipEvent(initiator=initiator, 
                                ini_object_pk=obj.pk,
                                ini_content_type=ini_c_type)
        rel.full_clean()
        rel.save()
        
def relationship_event_del(obj, parent, **kwargs):
        ini_c_type = ContentType.objects.get_for_model(obj)
        if parent != None: parent_c_type = ContentType.objects.get_for_model(parent)
        initiator = kwargs.get('initiator',None)
        if initiator == None:
            try: initiator = obj.user 
            except: pass
        if parent != None:
        
            rel = RelationshipEvent.objects.get(initiator=initiator, 
                                ini_object_pk=obj.pk,
                                tar_object_pk=parent.pk)
            rel.delete()
    
    
    
relationship_event.connect(register_relationship_event)
delete_relationship_event.connect(relationship_event_del)

admin.site.register(RelationshipEvent)
admin.site.register(Subscription)
