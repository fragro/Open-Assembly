from django.contrib import admin
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.signals import comment_was_posted
from pirate_issues.callbacks import update_issue_comment_count
#from ModuleDeliberation.models import Comment
from django.utils.translation import ugettext as _
from pirate_forum.models import ForumBlob
from django import forms
from pirate_sources.models import URLSource
from pirate_core import FormMixin
from django.forms.extras import SelectDateWidget
import datetime
from markitup.widgets import MarkItUpWidget


class Problem(ForumBlob):
    #A specific issue of political concern. Are authors important?
    #This should be a oa-wikipage instance
    class Meta:
        verbose_name = _('problem')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = '/index.html#item' + "/_t" + str(content_type.pk) + "/_o" + str(self.pk)
        return path

    def get_verbose_name(self):
        return self._meta.verbose_name

    def is_root(self):
        return False

    def get_blob_key(self):
        return 'pro'

    def get_child_blob_key(self):
        return 'sol'


class Solution(ForumBlob):

    class Meta:
        verbose_name = _('solution')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = '/index.html#item' + "/_t" + str(content_type.pk) + "/_o" + str(self.pk)
        return path

    def get_verbose_name(self):
        return self._meta.verbose_name

    def __unicode__(self):
        return str(self.summary) + " : " + str(self.id)

    def is_root(self):
        return False

    def get_blob_key(self):
        return 'sol'


class Policy(ForumBlob):

    class Meta:
        verbose_name = _('policy')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = '/index.html#item' + "/_t" + str(content_type.pk) + "/_o" + str(self.pk)
        return path

    def get_verbose_name(self):
        return self._meta.verbose_name

    def is_root(self):
        return False

    def get_blob_key(self):
        return 'pol'


class EvidenceOfFraud(ForumBlob):

    accused = models.CharField(max_length=200)

    class Meta:
        verbose_name = _('fraud')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = '/index.html#item' + "/_t" + str(content_type.pk) + "/_o" + str(self.pk)
        return path

    def get_verbose_name(self):
        return self._meta.verbose_name

    def is_root(self):
        return False

    def get_blob_key(self):
        return 'fra'


class News(ForumBlob):

    link = models.ForeignKey(URLSource, blank=True, null=True)

    class Meta:
        verbose_name = _('news')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = '/index.html#item' + "/_t" + str(content_type.pk) + "/_o" + str(self.pk)
        return path

    def get_verbose_name(self):
        return self._meta.verbose_name

    def is_root(self):
        return False

    def get_blob_key(self):
        return 'new'


class InformativeMaterial(ForumBlob):

    link = models.ForeignKey(URLSource, blank=True, null=True)

    class Meta:
        verbose_name = _('material')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = '/index.html#item' + "/_t" + str(content_type.pk) + "/_o" + str(self.pk)
        return path

    def get_verbose_name(self):
        return self._meta.verbose_name

    def is_root(self):
        return False

    def get_blob_key(self):
        return 'mat'

class ApplicationIdea(ForumBlob):

    class Meta:
        verbose_name = _('app idea')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = '/index.html#item' + "/_t" + str(content_type.pk) + "/_o" + str(self.pk)
        return path

    def get_verbose_name(self):
        return self._meta.verbose_name

    def is_root(self):
        return False

    def get_blob_key(self):
        return 'app'


class LegalHelp(ForumBlob):

    class Meta:
        verbose_name = _('legal help')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = '/index.html#item' + "/_t" + str(content_type.pk) + "/_o" + str(self.pk)
        return path

    def get_verbose_name(self):
        return self._meta.verbose_name

    def is_root(self):
        return False

    def get_blob_key(self):
        return 'leg'


class RightsViolation(ForumBlob):

    class Meta:
        verbose_name = _('rights violation')

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        path = '/index.html#item' + "/_t" + str(content_type.pk) + "/_o" + str(self.pk)
        return path

    def get_verbose_name(self):
        return self._meta.verbose_name

    def __unicode__(self):
        return str(self.summary) + " : " + str(self.id)

    def is_root(self):
        return False

    def get_blob_key(self):
        return 'rig'

###SIGNALS
comment_was_posted.connect(update_issue_comment_count)

###FORMS GO HERE TO MAKE USE OF GET_MODEL


class ProblemForm(forms.ModelForm, FormMixin):

    def save(self, commit=True):
        newo = super(ProblemForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
            newo.child = ContentType.objects.get_for_model(Solution)
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Problem
        exclude = ('parent', 'parent_pk', 'parent_type',
            'user', 'child', 'children', 'permission_req',
            'created_dt', 'modified_dt')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_problem_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),label="Title") 
    description = forms.CharField(widget=MarkItUpWidget(),label="Description")
    location = forms.CharField(label="Location", max_length=100,
              widget=forms.TextInput( 
                attrs={'size': '50', 'class': 'inputText'}),required=False)
    deadline_dt = forms.DateField(widget=SelectDateWidget(), required=False, label="Deadline")



class LegalHelpForm(forms.ModelForm, FormMixin):

    def save(self, commit=True):
        newo = super(LegalHelpForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
            newo.child = ContentType.objects.get_for_model(Solution)
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Problem
        exclude = ('parent', 'parent_pk', 'parent_type',
            'user', 'child', 'children', 'permission_req',
            'created_dt', 'modified_dt')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_problem_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'}),label="Title") 
    description = forms.CharField(widget=MarkItUpWidget(),label="Description")


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
        exclude = ('parent', 'parent_pk', 'parent_type',
                    'user', 'child', 'children', 'permission_req',
                    'created_dt', 'modified_dt', 'deadline_dt')

    #need to grab user from authenticatio
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_solution_form")
    summary = forms.CharField(max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), label="Title")
    description = forms.CharField(widget=MarkItUpWidget(), label="Description")


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


class EvidenceOfFraudForm(forms.ModelForm, FormMixin):

    def save(self, commit=True):
        newo = super(EvidenceOfFraudForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = EvidenceOfFraud
        exclude = ('parent', 'parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt' , 'modified_dt' , 'deadline_dt')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_policy_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class':'inputText'}),label="Title") 
    description = forms.CharField(widget=MarkItUpWidget(),label="Details of Fraud")
    accused = forms.CharField(label="Accused Party", max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), required=False)


class RightsViolationForm(forms.ModelForm, FormMixin):

    def save(self, commit=True):
        newo = super(RightsViolationForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = EvidenceOfFraud
        exclude = ('parent', 'parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt' , 'modified_dt' , 'deadline_dt')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_rightsviolation_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}),label="Summary of Violation") 
    description = forms.CharField(widget=MarkItUpWidget(),label="Details of Rights Violation")
    accused = forms.CharField(label="Accused Party", max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), required=False)


class NewsForm(forms.ModelForm, FormMixin):

    def save(self, commit=True):
        newo = super(NewsForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = News
        exclude = ('link', 'parent', 'parent_pk', 'parent_type', 'user', 'child', 'children', 'permission_req', 'created_dt', 'modified_dt' , 'deadline_dt')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_news_form")
    summary = forms.CharField(max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), label="Title")
    description = forms.CharField(widget=MarkItUpWidget(), label="Description of News")
    link = forms.CharField(label="News Link", max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), required=True)


class InformativeMaterialForm(forms.ModelForm, FormMixin):

    def save(self, commit=True):
        newo = super(InformativeMaterialForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = InformativeMaterial
        exclude = ('link', 'parent', 'parent_pk', 'parent_type', 'user',
                'child', 'children', 'permission_req', 'created_dt',
                'modified_dt', 'deadline_dt')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_info_form")
    summary = forms.CharField(max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), label="Title")
    description = forms.CharField(widget=MarkItUpWidget(), label="Description of Material")
    link = forms.CharField(label="Link to Material", max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), required=False)


class ApplicationIdeaForm(forms.ModelForm, FormMixin):

    def save(self, commit=True):
        newo = super(ApplicationIdeaForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = InformativeMaterial
        exclude = ('link', 'parent', 'parent_pk', 'parent_type',
                'user', 'child', 'children', 'permission_req',
                    'created_dt', 'modified_dt', 'deadline_dt')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_info_form")
    summary = forms.CharField(max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), label="Title")
    description = forms.CharField(widget=MarkItUpWidget(), label="Description of Material")

admin.site.register(InformativeMaterial)
admin.site.register(EvidenceOfFraud)
admin.site.register(News)
admin.site.register(Problem)
admin.site.register(Solution)
admin.site.register(Policy)
