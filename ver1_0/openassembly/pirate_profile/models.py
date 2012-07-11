from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from pirate_core import HttpRedirectException, namespace_get, FormMixin
from pirate_sources.models import IMGSource
from pirate_social.models import Location
from pirate_core.middleware import TYPE_KEY, OBJ_KEY


class Profile(models.Model):
    avatar = models.ForeignKey(IMGSource, blank=True, null=True)
    about_me = models.TextField(max_length=1000, default="", blank=True)
    birth_date = models.DateTimeField('birth_date', blank=True, null=True)
    user = models.ForeignKey(User)
    receive_emails = models.BooleanField(default=True)
    timezone = models.CharField(max_length=50)

    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        content_type2 = ContentType.objects.get_for_model(self.user)
        path = "/index.html#user/" + TYPE_KEY + str(content_type2.pk) + "/" + OBJ_KEY + str(self.user.pk)
        return path

admin.site.register(Profile)
