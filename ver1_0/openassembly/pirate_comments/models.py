from django.db import models
from django import template
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import settings

from django.template import Context, Template

#from ModuleDeliberation.models import Comment
from django.utils.translation import ugettext as _


class Comment(models.Model):
    user = models.ForeignKey(User)
    submit_date = models.DateTimeField('date_published')
    text = models.TextField(max_length=1200)
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_set_for_pirate_%(class)s")
    object_pk = models.CharField(_('object ID'), max_length=100)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    reply_to = models.ForeignKey('self', related_name="comment_parent", null=True)
    is_leaf = models.BooleanField()
    is_root = models.BooleanField()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('comment')

    def __unicode__(self):
        return self.user.username + ":" + str(self.submit_date)

    def get_absolute_url(self):
        t = Template("{% load pp_url%}{% pp_url template='detail.html' object=object scroll_to=scroll_to %}")
        c = Context({"object": self.content_object, 'scroll_to': 'comment' + str(self.pk)})
        return settings.DOMAIN + t.render(c)


def get_children(object_pk, cur_comment):
    get_list = []
    comments = Comment.objects.all()
    comments = comments.filter(object_pk=object_pk, is_root=False, reply_to=cur_comment)
    comments = comments.order_by('-submit_date')

    for c in comments:
        if c.is_leaf:
            get_list.append(c)
        else:
            get_list.append(get_children(object_pk, c))
    return [cur_comment, get_list]


def get_comments(parent, start, end, dimension, ctype_list):
    object_pk = parent.pk
    comment_tree = []

    comments = Comment.objects.all()
    comments = comments.filter(object_pk=object_pk, is_root=True, is_deleted=False)
    comments = comments.order_by('-submit_date')
    count = comments.filter(is_deleted=False).count()

    for c in comments:
        if c.is_leaf:
            comment_tree.append(c)
        else:
            comment_tree.append(get_children(object_pk, c))
    return comment_tree, count
