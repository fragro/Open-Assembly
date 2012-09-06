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

from pirate_forum.tasks import set_to_read

from collections import defaultdict
import datetime
from pirate_signals.models import notification_send

from django.shortcuts import get_object_or_404

from pirate_core.views import HttpRedirectException, namespace_get

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_messages')


@block
def pp_has_mail(context, nodelist, *args, **kwargs): 
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    reset = kwargs.get('reset', None)

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
    start = kwargs.get('start', None)
    end = kwargs.get('end', None)
    get_new = kwargs.get('get_new', None)

    if user.is_authenticated():
        if start is None or end is None:
            start = 0
            end = 20
        else:
            try:
                start = int(start)
                end = int(end)
            except:
                raise ValueError('start and end arguments must be of integer type')
        count = 0
        
        notes = Notification.objects.all()
        readnotes = notes.filter(receiver=user, is_read=True)
        count += readnotes.count()
        readnotes = readnotes.order_by('-submit_date')

        namespace['notifications'] = list(readnotes[start:end])

        unotes = notes.filter(receiver=user, is_read=False)
        count += unotes.count()
        namespace['unreadcount'] = unotes.count()
        notes = notes.order_by('-submit_date')

        namespace['unreadnotifications'] = list(unotes)
        

        mesnotes = list(unotes)
        retnotes = process_notes(mesnotes, "unread")

        retnotes.extend(process_notes(readnotes, "read"))

        set_to_read.apply_async(args=[unotes])

        namespace['notifications'] = retnotes

    else:
        count = 0
    namespace['count'] = count

    output = nodelist.render(context)
    context.pop()

    return output

#process the notes, aggregate messages with a common sender together
def process_notes(mesnotes, t):
    ctype = ContentType.objects.get_for_model(Message)
    retnotes = []
    messages = {}
    for i in mesnotes:
        if i.content_type == ctype:
            if i.sender_pk in messages:
                messages[i.sender_pk] = (messages[i.sender_pk][0], messages[i.sender_pk][1] + 1, t)
            else:
                messages[i.sender_pk] = (i, 1, t)
        else:
            retnotes.append((i, 0, t))

    retnotes.extend(messages.values())
    return retnotes

