from django import template
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from pirate_messages.models import Notification, Message
from django.db import transaction
from django.middleware import csrf
from django.contrib.contenttypes.models import ContentType
from pirate_profile.models import Profile
from django.utils.encoding import smart_str
from pirate_core.helpers import clean_html
from pirate_forum.models import get_rangelist

from pirate_messages.tasks import set_to_read

from collections import defaultdict
import datetime
from pirate_signals.models import notification_send

from django.shortcuts import get_object_or_404

from pirate_core.views import HttpRedirectException, namespace_get
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_messages')


@block
def pp_has_mail(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)

    notes = Notification.objects.filter(receiver=user, is_read=False)

    unread = Message.objects.filter(read=False, receiver=user)

    count = len(notes) + len(unread)

    if count == 0:
        has_mail = False
    else:
        has_mail = True
    namespace['has_mail'] = has_mail
    namespace['count'] = count

    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_notification_unread_list_get(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    reset = kwargs.get('reset', None)
    notes = Notification.objects.all()
    notes = notes.filter(receiver=user, is_read=False)
    notes = notes.order_by('-submit_date')
    if reset == None:
        for i in notes:
            i.is_read = True
            i.save()
    namespace['notifications'] = notes
    namespace['count'] = len(notes)

    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_notification_read_list_get(context, nodelist, *args, **kwargs): 
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)

    notes = Notification.objects.all()
    notes = notes.filter(receiver=user, is_read=True)
    notes = notes.order_by('-submit_date')

    namespace['notifications'] = notes


@block
def pp_notification_list_get(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    page = kwargs.get('page', 1)
    if page is None:
        page = 1
    if user.is_authenticated():

        notes = Notification.objects.all()
        notes = notes.filter(receiver=user)
        count = notes.count()
        notes = notes.order_by('-submit_date')

        paginator = Paginator(notes, 10)

        try:
            notes = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            notes = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            notes = paginator.page(paginator.num_pages)
        except:
            raise

        namespace['notifications'] = notes

    else:
        count = 0
    namespace['count'] = count

    output = nodelist.render(context)
    context.pop()

    return output


