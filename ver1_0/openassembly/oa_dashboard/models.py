from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.contrib import admin


class DashboardPanel(models.Model):
    """This platform model contains a list of ids and a model type
        for each user"""
    user = models.ForeignKey(User,
            verbose_name=_('user'), blank=True,
            null=True, related_name="%(class)s_ratings")
    plank = models.CharField(max_length=200)
    boardname = models.CharField(max_length=64, blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    zoom_x = models.IntegerField(blank=True, null=True)
    zoom_y = models.IntegerField(blank=True, null=True)

    dashboard_id = models.IntegerField()

    def __unicode__(self):
        return str(self.user.username) + ' - ' + str(self.plank) + ' - ' + str(self.priority)


# Create your models here.
