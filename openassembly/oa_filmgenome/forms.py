from django import forms
from django.forms.extras import SelectDateWidget
from pirate_issues.models import Problem, Solution, Policy
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
    
