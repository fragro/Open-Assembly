from django import forms
import datetime

class BlobForm(forms.Form):
    '''
    This form is used to allow creation and modification of issue objects.  
    It extends FormMixin in order to provide a create() class method, which
    is used to process POST, path, and object variables in a consistant way,
    and in order to automatically provide the form with a form_id.
    '''

    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),initial="") 
    description = forms.CharField(widget=forms.Textarea,initial="")   
    location = forms.CharField(label="text", max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),required=False,initial="")
    deadline_date = forms.DateField(required=False,initial="")
    deadline_time = forms.TimeField(required=False,initial="")
