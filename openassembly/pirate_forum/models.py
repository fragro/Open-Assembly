from django.db import models
from django import template
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.comments.signals import comment_was_posted
from pirate_permissions.models import Permission
from django.utils.translation import ugettext as _
from djangotoolbox.fields import ListField
from django.db.models import get_model, get_app
from pirate_core.middleware import TYPE_KEY, OBJ_KEY
from django.template import Context, Template


from django import forms
import random
import datetime
import pytz

from pirate_core.fields import JqSplitDateTimeField
from pirate_core.widgets import JqSplitDateTimeWidget
from django.template.defaultfilters import slugify

from markitup.widgets import MarkItUpWidget


def get_pretty_url(ctype_pk, obj_pk):
    ctype = ContentType.objects.get(pk=ctype_pk)
    obj = ctype.get_object_for_this_type(pk=obj_pk)
    try:
        key = slugify(obj.__unicode__())
        val, is_new = cached_url.objects.get_or_create(common_summary=key, obj_pk=obj_pk, ctype_pk=ctype_pk)
        if is_new:
            #validate to ensure this is a unique slug, otherwise increment til unique
            prevs = cached_url.objects.filter(common_summary=key)
            cnt = prevs.count()
            #if this is not a unique slug/url
            if cnt > 1:
                val.slug = key + str(cnt)
            else:
                val.slug = key
            val.save()
        #cache.set('/' + key, (ctype_pk, obj_pk))
    except:
        raise
    return val.slug


def reverse_pretty_url(obj_str):
    val, is_new = cached_url.objects.get_or_create(slug=obj_str)
    if is_new == True:
        raise ValueError(obj_str)
    return val.ctype_pk, val.obj_pk


class cached_url(models.Model):
    common_summary = models.CharField(max_length=200)
    slug = models.CharField(max_length=100)
    obj_pk = models.CharField(max_length=30)
    ctype_pk = models.CharField(max_length=30)

    def __unicode__(self):
        return self.slug


def get_rangelist(start, end, count):
    """Retrieves a rangelist for pagination
"""
    if start is not None and end is not None:
        if count != 0 and not (start == 0 and count < end):
            start = int(start)
            end = int(end)
            cnt = end - start
            rangelist = []
            div = int(start) / count + 1
            multiple = round(div, 0)
            start_range = int(count * multiple)
            n = 1
            for itr in range(0, start_range + count, 20):
                if itr < count:
                    rangelist.append([itr, itr + cnt, n])
                    n += 1
            return rangelist
        return []


def get_children(parent, start, end, dimension, ctype_list):

    if parent.child is not None:
        mm = parent.child.model_class()
        c = mm.objects.filter(parent_pk=parent.pk)
        count = c.count()
        return c[start:end], count
    return [], 0


class DimensionManager(models.Manager):
    def register(self, **kwargs):
        name = kwargs.get('name', None)
        key = kwargs.get('key', None)
        mcn = kwargs.get('model_class_name', None)
        ap = kwargs.get('app_label', None)
        fcm = kwargs.get('form_class_name', None)
        is_content = kwargs.get('is_content', True)
        is_child = kwargs.get('is_child', False)
        is_admin = kwargs.get('is_admin', False)
        help_text = kwargs.get('help_text', '')
        self.get_or_create(name=name, key=key, app_label=ap,
                            model_class_name=mcn, form_class_name=fcm, help_text=help_text,
                            is_content=is_content, is_child=is_child, is_admin=is_admin)


class ForumDimension(models.Model):
    key = models.CharField(max_length=200)
    name = models.CharField(max_length=200, blank=True, null=True)
    help_text = models.CharField(max_length=400, blank=True, null=True)
    app_label = models.CharField(max_length=60)
    model_class_name = models.CharField(max_length=60)
    form_class_name = models.CharField(max_length=60)
    is_content = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_child = models.BooleanField(default=False)

    objects = DimensionManager()

    def get_form(self):
        app = get_app(self.app_label)
        return getattr(app, self.form_class_name)

    def get_model(self):
        return get_model(self.app_label, self.model_class_name)

    def __unicode__(self):
        return str(self.name) + ' : ' + str(self.key) 


class DimensionTracker(models.Model):
    object_pk = models.CharField(max_length=100)
    dimension = models.ForeignKey(ForumDimension)
    children = models.IntegerField(default=0)

    def __unicode__(self):
        return str(self.dimension) + ' : ' + str(self.object_pk) + ' : ' + str(self.children)


class ForumBlob(models.Model):
    summary = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(max_length=5000, blank=True, null=True)

    parent_type = models.ForeignKey(ContentType, verbose_name=_('parent content type'),
                                            related_name="%(app_label)s_%(class)s_parent",
                                            blank=True, null=True)
    parent_pk = models.CharField(_('Parent PK'), max_length=100, blank=True, null=True)
    parent = generic.GenericForeignKey(ct_field="parent_type", fk_field="parent_pk")
    parent_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    child = models.ForeignKey(ContentType, verbose_name=_('child content type'),
                                            related_name="%(app_label)s_%(class)s_child",
                                            blank=True, null=True)
    children = models.IntegerField(default=0, blank=True, null=True)
    created_dt = models.DateTimeField(_('Date Published'), auto_now_add=True)
    modified_dt = models.DateTimeField(_('Date Modified'), blank=True, null=True)
    #deadline_dt = models.DateTimeField(_('Date Deadline'), blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    forumdimension = models.ForeignKey(ForumDimension, blank=True, null=True)
    #classification_model = models.ForeignKey(ClassModel)
    #location = models.CharField(max_length=100, blank=True, null=True)
    permission_req = models.ForeignKey(Permission, blank=True, null=True)
    #pad = models.BooleanField(default=False, verbose_name="Include EtherPad (this allows users to collaboratively edit)")

    def __unicode__(self):
        return self.summary

    def taggable(self):
        return True

    def get_absolute_url(self):
        t = Template("{% load pp_url%}{% pp_url template='detail.html' object=object %}")
        c = Context({"object": self})
        return t.render(c)

    class Meta:
        abstract = True

    def get_blob_key(self):
        return self.forumdimension.key


class Question(ForumBlob):

    class Meta:
        verbose_name = _('question')

    def __unicode__(self):
        return self.summary

    def get_verbose_name(self):
        return self._meta.verbose_name

    def taggable(self):
        return True

    def get_child_blob_key(self):
        return 'nom'


class Nomination(ForumBlob):
    #for random sorting of voting candidates
    random = models.FloatField(default=0)

    class Meta:
        verbose_name = _('nomination')

    def __unicode__(self):
        return self.summary

    def get_verbose_name(self):
        return self._meta.verbose_name

    def taggable(self):
        return True

    def is_child(self):
        return True

    def get_blob_key(self):
        return 'nom'


class View(models.Model):
    object_pk = models.IntegerField()
    num = models.IntegerField(default=0)
    ips = ListField(models.CharField(max_length=16))
    users = ListField(models.CharField(max_length=30))

    def __unicode__(self):
        return str(self.object_pk) + ' : ' + str(self.num)


def create_view(username, addr, obj_id):
    #defers creating view to optimize
    if obj_id is not None:
        v, is_new = View.objects.get_or_create(object_pk=obj_id)
        if not is_new:
            v.num += 1
            v.ips.append(addr)
            v.users.append(username)
        else:
            v.ips.append(addr)
            v.users.append(username)
            v.num = 1
        v.save()

    '''
    This form is used to allow creation and modification of issue objects.
    It extends FormMixin in order to provide a create() class method, which
    is used to process POST, path, and object variables in a consistant way,
    and in order to automatically provide the form with a form_id.
    '''

votechoices = (
    ('SS', 'Single Winner Timed Decision'),
    ('PE', 'Persistent Temperature Check'),
)


class BlobForm(forms.ModelForm):

    def save(self, commit=True):
        newo = super(BlobForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
            ctype = ContentType.objects.get_for_model(Nomination)
            newo.child = ctype
            newo.children = 0
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Question
        exclude = ('parent', 'parent_pk', 'parent_type',
            'user', 'child', 'children', 'permission_req',
            'created_dt', 'modified_dt', 'forumdimension')

    summary = forms.CharField(max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), initial="")
    description = forms.CharField(widget=MarkItUpWidget(
                attrs={'cols': '20', 'rows': '10'}), initial="")

    end_of_nomination_phase = JqSplitDateTimeField(widget=JqSplitDateTimeWidget(attrs={'date_class': 'datepicker', 'time_class': 'timepicker'}))
    decision_time = JqSplitDateTimeField(widget=JqSplitDateTimeWidget(attrs={'date_class': 'datepicker', 'time_class': 'timepicker'}))
    timezone = forms.ChoiceField(label="Time Zone:", choices=[(i, i) for i in pytz.common_timezones])
    winners = forms.IntegerField(required=False, help_text="Number of responses to accept, leave this blank to accept all responses.")


class BlobEditForm(forms.ModelForm):

    def save(self, commit=True):
        newo = super(BlobEditForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
            ctype = ContentType.objects.get_for_model(Nomination)
            newo.child = ctype
            newo.children = 0
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Question
        exclude = ('parent', 'parent_pk', 'parent_type',
            'user', 'child', 'children', 'permission_req',
            'created_dt', 'modified_dt', 'forumdimension')

    summary = forms.CharField(max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), initial="")
    description = forms.CharField(widget=MarkItUpWidget(
                attrs={'cols': '20', 'rows': '10'}), initial="")


class NominationForm(forms.ModelForm):

    def save(self, commit=True):
        newo = super(NominationForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
            newo.random = random.random()
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Nomination
        exclude = ('parent', 'parent_pk', 'parent_type',
            'user', 'child', 'children', 'permission_req',
            'created_dt', 'modified_dt', 'forumdimension', 'random')

    summary = forms.CharField(max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), initial="")
    description = forms.CharField(widget=forms.Textarea(), initial="")

admin.site.register(View)
admin.site.register(ForumDimension)
admin.site.register(DimensionTracker)
admin.site.register(Question)
admin.site.register(Nomination)
admin.site.register(cached_url)
