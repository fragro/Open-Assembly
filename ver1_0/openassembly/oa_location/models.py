from djangotoolbox.fields import EmbeddedModelField
from django_mongodb_engine.contrib import MongoDBManager
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.db import models
from django.utils.translation import ugettext as _
from django.contrib import admin


"""
This Django class breaks to the lower level pymongo to allow for GoeSpatial Queries
"""


class Point(models.Model):
	latitude = models.FloatField()
	longtitude = models.FloatField()


class Location(models.Model):
	description = models.CharField(max_length=200)

	def __unicode__(self):
		return str(self.description)


class Place(models.Model):
	parent_pk = models.IntegerField(_('Parent PK'), blank=True, null=True)
	summary = models.ForeignKey('Location', blank=True, null=True)
	object_pk = models.CharField(_('object ID'), max_length=100)
	content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
	content_type = models.ForeignKey(ContentType,
									  verbose_name=_('content type'),
									  related_name="content_type_set_for_%(class)s")
	location = EmbeddedModelField(Point)

	objects = MongoDBManager()

	def __unicode__(self):
		return str(self.summary.description)



class LocationForm(forms.Form):

	form_id = forms.CharField(widget=forms.HiddenInput(), initial="oa_location_form")
	description = forms.CharField(label="Description")

