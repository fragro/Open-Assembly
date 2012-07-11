from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime
import django.dispatch
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from pirate_signals.models import vote_created

# Create your models here.


#Generic flag concept, contains information concerning flags 
#should be unique for flag_type and object_pk
class Flag(models.Model):
    
    parent_pk = models.IntegerField() #id for consensus
    submit_date = models.DateTimeField(_('date/time submitted'),auto_now_add=True)
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_set_for_%(class)s")
    object_pk = models.CharField(_('object ID'), max_length=100)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    #number of children
    votes = models.IntegerField(default=0)
    counters = models.IntegerField(default=0)
    flag_type = models.CharField(max_length=100)
    
    def __unicode__(self):
        return "%s: %s: %s" % (self.flag_type, self.object_pk, self.votes-self.counters)
    
#stores user related logical fallacy flagging info    
class UserFlag(models.Model):
    user = models.ForeignKey(User)
    flag = models.ForeignKey(Flag, blank=True, null=True)
    mode = models.BooleanField()
    
    def __unicode__(self):
        return "%s: %s: %s" % (self.user, self.flag, self.mode)


admin.site.register(Flag)
admin.site.register(UserFlag)
