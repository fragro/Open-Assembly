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
    description = forms.CharField(widget=forms.Textarea, label="Description")
    


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
                attrs={'size':'50', 'class':'inputText'}), label="Summary of Argument") 
    description = forms.CharField(widget=forms.Textarea, label="Description")
    
    
    
    
