from django import forms
from pirate_actions.models import Action
from pirate_topics.models import Topic
from pirate_core.forms import FormMixin
from markitup.widgets import MarkItUpWidget
from pirate_core.widgets import SelectTimeWidget, HorizRadioRenderer
from django.forms.extras import SelectDateWidget
import datetime
from oa_suggest.models import Bug, Suggestion
   

class BugForm(forms.ModelForm, FormMixin):
    
    def save(self, commit=True):
        newo = super(BugForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Bug
        exclude = ('parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt' , 'modified_dt', 'deadline_dt' )
               
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_bug_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),label="Title") 
    description = forms.CharField(widget=MarkItUpWidget(),label="Bug Description")
    location = forms.CharField(label="URL that caused error", max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),required=False)
    
    
class SuggestionForm(forms.ModelForm, FormMixin):
    
    def save(self, commit=True):
        newo = super(SuggestionForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Suggestion
        exclude = ('parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt' , 'modified_dt', 'deadline_dt' )
               
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_suggestion_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),label="Title") 
    description = forms.CharField(widget=MarkItUpWidget(),label="Description of Feature or Suggestion")
    
        
