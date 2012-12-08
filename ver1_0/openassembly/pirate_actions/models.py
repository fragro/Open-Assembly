from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
#from ModuleDeliberation.models import Comment
from django.utils.translation import ugettext as _ 
from pirate_forum.models import ForumBlob


class Event(ForumBlob):

    date = models.DateTimeField(_("Date"), blank=True, null=True)
    time_start = models.TimeField(_("Time Start"), blank=True, null=True)
    time_end = models.TimeField(_("Time End"), blank=True, null=True)
    address = models.CharField(max_length=300)

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


class Action(models.Model):

    user = models.ForeignKey(User)
    created_dt = models.DateTimeField(auto_now=True, blank=True, null=True)
    parent_pk = models.CharField(_('parent PK'), max_length=100)
    object_pk = models.CharField(_('object ID'), max_length=100)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_set_for_%(class)s")
    description = models.CharField(max_length=5000)

    class Meta:
        verbose_name = _('action')

    def __unicode__(self):
        return 'action from ' + str(self.user.username) + ' on ' + str(self.content_object)

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


########################################FORMS

from django import forms
from django.utils.translation import ugettext as _


class ActionForm(forms.Form):

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_action_form")
    description = forms.CharField(widget=forms.widgets.Textarea, label="Description")
