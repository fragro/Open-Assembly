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


class ProblemForm(forms.ModelForm, FormMixin):
    
    def save(self, commit=True):
        newo = super(ProblemForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
            newo.child = ContentType.objects.get_for_model(Solution)
            children = 0
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Problem
        exclude = ('parent','parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt' , 'modified_dt' )
       
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_problem_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),label="Title") 
    description = forms.CharField(widget=MarkItUpWidget(),label="Description")
    location = forms.CharField(label="Location", max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),required=False)
    deadline_dt = forms.DateField(widget = SelectDateWidget(),required=False,label="Deadline")

    
class SolutionForm(forms.ModelForm, FormMixin):
    '''
    This form is used to allow creation and modification of issue objects.  
    It extends FormMixin in order to provide a create() class method, which
    is used to process POST, path, and object variables in a consistant way,
    and in order to automatically provide the form with a form_id.
    '''

    def save(self, commit=True):
        new_issue = super(SolutionForm, self).save(commit=commit)
        return new_issue

    class Meta:
        model = Solution
        exclude = ('parent', 'parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt' , 'modified_dt', 'deadline_dt' )
        
    #need to grab user from authenticatio
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_solution_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}), label="Title") 
    description = forms.CharField(widget=MarkItUpWidget(),label="Description")
    
      
class PolicyForm(forms.ModelForm, FormMixin):
    
    def save(self, commit=True):
        newo = super(PolicyForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Policy
        exclude = ('parent', 'parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt' , 'modified_dt' , 'deadline_dt')
        
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_policy_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),label="Title") 
    description = forms.CharField(widget=MarkItUpWidget(),label="Details of Policy")
    location = forms.CharField(label="Location", max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),required=False)

    
        
