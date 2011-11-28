from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from tagging.models import Tag
from django.utils.translation import ugettext as _
from pirate_forum.models import ForumBlob

    
#Stance is a type of argument -- probably specified by admin
class Stance(models.Model):
    arg = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.arg

#An argument of {arg_type} that is attached to an Issue 
#This should be a oa-wikipage instance
class Argument(ForumBlob):
    stance = models.ForeignKey(Stance)

    class Meta:
        verbose_name = _('argument')
        #help_text = _('Supply an Argument for your position.')
    
    def __unicode__(self):
        return self.summary

    def get_verbose_name(self):
        return self._meta.verbose_name
    
    def get_blob_key(self):
        return 'arg'

    def taggable(self):
        return True
     
admin.site.register(Stance)
admin.site.register(Argument)

from django import forms
from django.forms.extras import SelectDateWidget
from pirate_deliberation.models import Argument, Stance
from pirate_topics.models import Topic
from pirate_forum.forms import BlobForm
from pirate_core.forms import FormMixin
from pirate_core.widgets import HorizRadioRenderer
from django.contrib.contenttypes.models import ContentType
import datetime
from markitup.widgets import MarkItUpWidget


class NayArgumentForm(forms.ModelForm, FormMixin):
    
    def save(self, commit=True):
        newo = super(NayArgumentForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        newo.modified_dt = datetime.datetime.now()
        newo.stance, news = Stance.objects.get_or_create(arg='nay')
        newo.save()
        return newo

    class Meta:
        model = Argument
        exclude = ('parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt' , 'modified_dt', 'deadline_dt', 'location', 'stance' )
               
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_argument_form_nay")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),label="Summary of Argument") 
    description = forms.CharField(widget=forms.Textarea(attrs={'size':'100'}), label="Description")
    


class YeaArgumentForm(forms.ModelForm, FormMixin):
    
    def save(self, commit=True):
        newo = super(YeaArgumentForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        newo.modified_dt = datetime.datetime.now()
        newo.stance, news = Stance.objects.get_or_create(arg='yea')
        newo.save()
        return newo

    class Meta:
        model = Argument
        exclude = ('parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt' , 'modified_dt', 'deadline_dt', 'location', 'stance' )
               
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_argument_form_yea")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),label="Summary of Argument") 
    description = forms.CharField(widget=forms.Textarea(attrs={'size':'100'}), label="Description")


def get_argument_list(parent, start, end, dimension, ctype_list):
    arg_list = Argument.objects.all()
    arg_type, created = Stance.objects.get_or_create(arg=dimension)

    if isinstance(start, int) and isinstance(end, int):
        try:
            rng = (int(start), int(end))
        except:
            rng = None
        if not rng or len(rng) != 2:
            raise ValueError("The argument 'start=' and 'end=' to the pp_get_argument_list tag must be "
                                 "provided either in the form of an int")
    else:
        rng = (0, 20)
    if parent:
        arg_list = arg_list.filter(parent_pk=parent.id).order_by('-created_dt')
    if arg_type:
        arg_list = arg_list.filter(stance=arg_type)
    #get total number of arguments
    count = arg_list.count()
    if rng:
        arg_list = arg_list[start:end]
    if arg_list == None:
        arg_list = []
    return arg_list, count
