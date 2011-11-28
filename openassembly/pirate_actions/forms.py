from django import forms
from pirate_actions.models import Action
from pirate_topics.models import Topic
from pirate_core.forms import FormMixin
from markitup.widgets import MarkItUpWidget
from pirate_core.widgets import SelectTimeWidget, HorizRadioRenderer
from django.forms.extras import SelectDateWidget
import datetime
   
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
    
        
