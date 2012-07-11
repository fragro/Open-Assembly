from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import SuspiciousOperation
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib import admin
from django.utils.translation import ugettext as _

from pirate_reputation.models import ReputationDimension


class PermissionsGroup(models.Model):
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=300)
    #users = models.ManyToManyField(User) #django-nonrel does not support ManyToMany
    is_active = models.BooleanField()

    created_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.name)


class Permission(models.Model):
    user = models.ForeignKey(User)
    name = models.SlugField()
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_permission_for_%(class)s")
    object_pk = models.CharField(_('object ID'), max_length=100)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    component_membership_required = models.BooleanField(default=False)
    permissions_group = models.ForeignKey(PermissionsGroup)

    def __unicode__(self):
        return str(self.user) + ': ' + str(self.content_type) + ' : ' + str(self.object_pk)


class ReputationSpec(models.Model):
    dimension = models.ForeignKey(ReputationDimension, null=True)
    threshold = models.IntegerField()
    permissions_group = models.ForeignKey(PermissionsGroup)

    def save(self):
        if self.dimension == None:
            self.dimension = ReputationDimension.objects.null_dimension()
        super(ReputationSpec, self).save()

admin.site.register(PermissionsGroup)
admin.site.register(Permission)
