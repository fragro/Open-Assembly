from django.db import models
from django import template
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
#from ModuleDeliberation.models import Comment
from django.utils.translation import ugettext as _ 
from pirate_forum.models import ForumBlob
from pirate_topics.models import Topic


class Event(ForumBlob):
    
    date = models.DateTimeField(_("Date"), blank=True,null=True)
    time_start = models.TimeField(_("Time Start"), blank=True,null=True)
    time_end = models.TimeField(_("Time End"), blank=True,null=True)
    address= models.CharField(max_length=300)

    class Meta:
        verbose_name = _('event')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = "/index.html#item" + "/_t" + str(content_type.pk) + "/_o" + str(self.pk)
        return path
    
    def get_verbose_name(self):
        return self._meta.verbose_name

    def is_action(self):
        return 'Attending Event'
    
    def is_root(self):
        return True
    
    def get_blob_key(self):
        return 'eve'
    
    def admin_only(self):
        return False
    
    def get_model_specific(self):
        return ((self._meta.get_field_by_name('date')[0].verbose_name, self.date),(self._meta.get_field_by_name('time_start')[0].verbose_name, self.time_start),(self._meta.get_field_by_name('time_end')[0].verbose_name, self.time_end),(self._meta.get_field_by_name('adress')[0].verbose_name, self.address))



class Boycott(ForumBlob):
    
    date = models.DateTimeField(_("Date"), blank=True,null=True)
    time_start = models.TimeField(_("Time Start"), blank=True,null=True)
    time_end = models.TimeField(_("Time End"), blank=True,null=True)
    target = models.CharField(_("Target Corporation"), max_length=300)
    product = models.CharField(_("Target Product"), max_length=300, blank=True, null=True)

    class Meta:
        verbose_name = _('boycott')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = "/index.html#item" + "/_t" + str(content_type.pk) + "/_o" + str(self.pk)
        return path

    def get_verbose_name(self):
        return self._meta.verbose_name
    
    def is_root(self):
        return True

    def get_blob_key(self):
        return 'boy'
    
    def admin_only(self):
        return False

    def get_model_specific(self):
        return ((self._meta.get_field_by_name('date')[0].verbose_name, self.date), (self._meta.get_field_by_name('time_start')[0].verbose_name, self.time_start),(self._meta.get_field_by_name('time_end')[0].verbose_name, self.time_end),(self._meta.get_field_by_name('target')[0].verbose_name, self.target),(self._meta.get_field_by_name('product')[0].verbose_name, self.product))


class Action(ForumBlob):

    date = models.DateField(_("Date"), blank=True, null=True)
    time_start = models.TimeField(_("Time Start"), blank=True, null=True)
    time_end = models.TimeField(_("Time End"), blank=True, null=True)

    class Meta:
        verbose_name = _('action')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = '/index.html#item' + "/_t" + str(content_type.pk) + "/_o" + str(self.pk)
        return path

    def get_verbose_name(self):
        return self._meta.verbose_name

    def is_action(self):
        return 'Take Action'

    def is_root(self):
        return True

    def get_blob_key(self):
        return 'act'

    def admin_only(self):
        return False

    def get_model_specific(self):
        return ((self._meta.get_field_by_name('date')[0].verbose_name, self.date), (self._meta.get_field_by_name('time_start')[0].verbose_name, self.time_start),(self._meta.get_field_by_name('time_end')[0].verbose_name, self.time_end))
        #return (self.date, self.time_start, self.time_end)


########################################FORMS

from django import forms
from pirate_topics.models import Topic
from pirate_core.forms import FormMixin
from markitup.widgets import MarkItUpWidget
from pirate_actions.models import Boycott
from pirate_core.widgets import SelectTimeWidget,HorizRadioRenderer
from django.forms.extras import SelectDateWidget
import datetime
from django.utils.translation import ugettext as _


class ActionForm(forms.ModelForm, FormMixin):
    
    def save(self, commit=True):
        newo = super(ActionForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Action
        exclude = ('parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt' , 'modified_dt', 'deadline_dt' )
               
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_event_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),label="Summary of Action") 
    description = forms.CharField(widget=MarkItUpWidget(),label="Call to Action Instructions")
    location = forms.CharField(label="City/State/Country Location", max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),required=False)
    date = forms.DateField(widget = SelectDateWidget(),required=False,label="Date")
    time_start = forms.TimeField(widget = SelectTimeWidget(),required=False,label="Time Start")
    time_end = forms.TimeField(widget = SelectTimeWidget(),required=False,label="Time End")
