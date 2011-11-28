from django.db import models
from django import template
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
#from ModuleDeliberation.models import Comment
from django.utils.translation import ugettext as _ 
from pirate_forum.models import ForumBlob
from pirate_sources.models import VideoSource

# Create your models here.


class Film(ForumBlob):
    
    video = models.ForeignKey(VideoSource, blank=True, null=True)

    class Meta:
        verbose_name = _('Film')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = '/index.html#' + "/_t" + str(content_type.pk) + "/_o" + str(self.pk) 
        return path
    
    def get_verbose_name(self):
        return self._meta.verbose_name
    
    def get_action_verb(self):
        return "filmed"
    
    def is_root(self):
        return False
    
    def get_blob_key(self):
        return 'fil'
    
    def get_child_blob_key(self):
        return 'sce'

    def admin_only(self):
        return True
    
class Scene(ForumBlob):

    class Meta:
        verbose_name = _('Scene')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = '/index.html#' + "/_t" + str(content_type.pk) + "/_o" + str(self.pk) 
        return path
    
    def get_verbose_name(self):
        return self._meta.verbose_name
    
    def is_root(self):
        return False
    
    def get_blob_key(self):
        return 'sce'
    
    def admin_only(self):
        return True

class FilmIdea(ForumBlob):

    class Meta:
        verbose_name = _('FilmIdea')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = '/index.html#' + "/_t" + str(content_type.pk) + "/_o" + str(self.pk) 
        return path
    
    def get_verbose_name(self):
        return self._meta.verbose_name
    
    def is_root(self):
        return False
    
    def get_blob_key(self):
        return 'fii'
    
    def __unicode__(self):
        return str(self.summary)
    
#admin.site.register(Film)
#admin.site.register(Scene)
#admin.site.register(FilmIdea)

#########################FORMS

from django import forms
from django.forms.extras import SelectDateWidget
from pirate_topics.models import Topic
from pirate_forum.forms import BlobForm
from pirate_core.forms import FormMixin
from pirate_core.widgets import HorizRadioRenderer
from django.contrib.contenttypes.models import ContentType
import datetime
from markitup.widgets import MarkItUpWidget
from oa_filmgenome.models import Film, Scene, FilmIdea


class FilmForm(forms.ModelForm, FormMixin):
    
    def save(self, commit=True):
        newo = super(FilmForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
            newo.child = ContentType.objects.get_for_model(Scene)
            children = 0
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Film
        exclude = ('parent','parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt' , 'modified_dt', 'deadline_dt' )
       
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_film_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'70', 'class':'inputText'}),label="Film Name")
    description = forms.CharField(widget=MarkItUpWidget(),label="Description/Credits")
    location = forms.CharField(label="Filming Location", max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'70', 'class':'inputText'}),required=False)
  
    
class SceneForm(forms.ModelForm, FormMixin):
    
    def save(self, commit=True):
        newo = super(SceneForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Scene
        exclude = ('parent','parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt' , 'modified_dt', 'deadline_dt' )
       
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_scene_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'70', 'class':'inputText'}),label="Summary of Scene") 
    description = forms.CharField(widget=MarkItUpWidget(),label="Embed Image, Video, and/or Description")
    location = forms.CharField(label="Location of Scene", max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'70', 'class':'inputText'}),required=False)
                
class FilmIdeaForm(forms.ModelForm, FormMixin):
    
    def save(self, commit=True):
        newo = super(FilmIdeaForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = FilmIdea
        exclude = ('parent','parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt' , 'modified_dt', 'deadline_dt' )
       
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_filmidea_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'70', 'class':'inputText'}),label="Title")
    description = forms.CharField(widget=MarkItUpWidget(attrs={'size':'70'}),label="Description of Film Idea")
    location = forms.CharField(label="Location of Idea if Applicable", max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'70', 'class':'inputText'}),required=False)
    

