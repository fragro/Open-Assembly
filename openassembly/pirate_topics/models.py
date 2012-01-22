from django.db import models
from django import template
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from pirate_core.middleware import TYPE_KEY, OBJ_KEY, START_KEY, END_KEY, DIM_KEY
from django.template import Context, Template

# First, define the Manager subclass.
class TopicManager(models.Manager):
    def get_query_set(self):
        return super(TopicManager, self).get_query_set().exclude(summary="__NULL__")


class NullManager(models.Manager):
    def null_dimension(self):
        return self.get_or_create(summary="__NULL__")[0]


class Topic(models.Model):
    #Topic: Category to place issues, includes parent and child for hierarchical topics
    summary = models.CharField(max_length=200, unique=True)
    shortname = models.CharField(max_length=23, unique=True)
    description = models.CharField(max_length=600, unique=True)
    submit_date = models.DateTimeField('date published', auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    children = models.IntegerField(_('Children'), default=0)
    solutions = models.IntegerField(_('Solution'), default=0)
    decisions = models.IntegerField(_('Solution'), default=0)
    more_info = models.CharField(max_length=200, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True, null=True)
    slug = models.CharField(max_length=200, blank=True, null=True)
    group_members = models.IntegerField(default=0)
    objects = NullManager()
    clean_objects = TopicManager()

    def __unicode__(self):
        return self.shortname

    def get_verbose_name(self):
        return 'topic'

    def is_root(self):
        return True

    def get_absolute_url(self):
        t = Template("{% load pp_url%}{% pp_url template='group.html' object=object %}")
        c = Context({"object": self})
        return t.render(c)

    def get_absolute_list_url(self):
        t = Template("{% load pp_url%}{% pp_url template='issues.html' object=object start=0 end=20 dimension='n' %}")
        c = Context({"object": self})
        return t.render(c)


class MyGroup(models.Model):
    topic = models.ForeignKey(Topic, blank=True, null=True)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return str(self.topic) + " : " + str(self.user.username)


class GroupSettings(models.Model):
    topic = models.ForeignKey(Topic, blank=True, null=True)
    stream = models.CharField(max_length=30, blank=True, null=True, help_text="Account name to Embed stream into navigation.")
    stream_provider = models.CharField(max_length=30, blank=True, null=True, help_text="Provider of streaming service.")
    open_group = models.BooleanField(default=True, help_text="If the group is open anyone can join, if it's closed they must be invited")
    percent_reporting = models.FloatField(default=.7, help_text="Percentage of members required to vote for pushing a set of solutions/answers to a ranked vote. Value represents a percentage for instance .7 is 70% of Members voting")
    consensus_percentage = models.FloatField(default=.8, help_text="For policies or proposals, what percentage of votes constitutes consensus when no blocks are present?")

    def __unicode__(self):
        return str(self.topic)


def get_topics(parent, start, end, dimension, ctype_list):

    #dimension can be children or number of group members
    if parent != None and isinstance(parent, Topic):
        topic_list = Topic.objects.filter(parent=parent)
    else:
        topic_list = Topic.objects.filter(parent=Topic.objects.null_dimension())
    if dimension == 'c':
        topic_list = topic_list.order_by('-children')
    elif dimension == 'n':
        topic_list = topic_list.order_by('-submit_date')
    elif dimension == 'h':
        topic_list = topic_list.order_by('-group_members')
    count = topic_list.count()
    if start is not None and end is not None:
        topic_list = topic_list[int(start):int(end)]
    return topic_list, count

admin.site.register(Topic)
admin.site.register(MyGroup)
admin.site.register(GroupSettings)
