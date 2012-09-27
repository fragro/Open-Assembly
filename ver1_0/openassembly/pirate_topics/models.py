from django.db import models
from django import template
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from pirate_core.middleware import TYPE_KEY, OBJ_KEY, START_KEY, END_KEY, DIM_KEY
from django.template import Context, Template

from celery.task import task
from tagging.models import Tag, TaggedItem

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
    description = models.CharField(max_length=2500, unique=True)
    submit_date = models.DateTimeField('date published', auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    children = models.IntegerField(_('Children'), default=0)
    solutions = models.IntegerField(_('Solution'), default=0)
    decisions = models.IntegerField(_('Solution'), default=0)
    more_info = models.CharField(max_length=200, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True, null=True)
    slug = models.CharField(max_length=200, blank=True, null=True)
    group_members = models.IntegerField(default=1)
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
        t = Template("{% load pp_url%}{% pp_url template='issues.html' object=object start=0 end=10 dimension='n' %}")
        c = Context({"object": self})
        return t.render(c)


class MyGroup(models.Model):
    topic = models.ForeignKey(Topic, blank=True, null=True)
    user = models.ForeignKey(User)
    created_dt = models.DateTimeField(blank=True, null=True, auto_now_add=True)

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


def get_users(parent, start, end, dimension, ctype_list):

    #if this object is a topic, get group members
    if parent != None and isinstance(parent, Topic):
        user_list = MyGroup.objects.filter(topic=parent)
        if dimension == 'n':
            user_list = user_list.order_by('-created_dt')
        count = user_list.count()
        if start is not None and end is not None:
            user_list = user_list[int(start):int(end)]
        return user_list, count
    else:
        user_list = User.objects.filter(is_active=True)
        count = user_list.count()
        if dimension == 'n':
            user_list = user_list.order_by('-date_joined')
        if dimension == 'j':
            user_list = user_list.order_by('-last_login')
        if dimension == 'a':
            user_list = user_list.order_by('username')
        if start is not None and end is not None:
            user_list = user_list[int(start):int(end)]
        return user_list, count


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
    elif dimension == 'o':
        topic_list = topic_list.order_by('submit_date')
    elif dimension == 'h':
        topic_list = topic_list.order_by('-group_members')
    elif dimension == 'a':
        topic_list = topic_list.order_by('-summary')
    count = topic_list.count()
    print dimension
    if start is not None and end is not None:
        topic_list = topic_list[int(start):int(end)]
    return topic_list, count


@task(ignore_result=True)
def add_group_tag(obj_pk, ctype_pk, tag):
    ctype = ContentType.objects.get(pk=ctype_pk)
    obj = ctype.get_object_for_this_type(pk=obj_pk)
    root = get_root(obj)
    #also add to the objects group so we can display group specific tags
    Tag.objects.add_tag(root, tag)


@task(ignore_result=True)
def del_group_tag(obj_pk, ctype_pk, tag):
    ctype = ContentType.objects.get(pk=ctype_pk)
    obj = ctype.get_object_for_this_type(pk=obj_pk)
    root = get_root(obj)
    #also add to the objects group so we can display group specific tags
    taggedobj = TaggedItem.objects.get(tag_name=tag, object_id=root.pk)
    taggedobj.delete()


def get_root(root):
    if root is not None:
        try:
            parent = root.parent
        except:
            try:
                parent = root.content_object
            except:
                return None
        while parent is not None:
            if parent.summary == '__NULL__':
                return root
            root = parent
            parent = parent.parent

