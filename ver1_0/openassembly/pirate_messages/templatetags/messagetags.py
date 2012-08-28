from django import template
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from pirate_messages.models import Message, MessageForm, Notification
from django.db import transaction
from django.middleware import csrf
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_str
#from ajaxapi.views import clean_html
from pirate_forum.models import get_rangelist
from django.contrib.auth.models import User

import datetime
from pirate_signals.models import notification_send

from django.shortcuts import get_object_or_404

from pirate_core.views import HttpRedirectException, namespace_get

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_messages')


@block
def pp_get_messages(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    sender = kwargs.get('sender')
    user = kwargs.get('user', None)
    start = kwargs.get('start', 0)
    end = kwargs.get('end', 10)
    newest = kwargs.get('newest', None)

    read = Message.objects.filter(read=True, receiver=user)

    unread = Message.objects.filter(read=False, receiver=user)

    if sender is not None:
        read = read.filter(sender=sender)
        unread = unread.filter(sender=sender)
        read = read.order_by('-created_dt')
        for mes in unread:
            mes.read = True
            mes.save()

    count = unread.count()
    rcount = read.count()

    if count == 0:
        has_mail = False
    else:
        has_mail = True

    namespace['has_mail'] = has_mail
    namespace['unreadcount'] = count
    namespace['readcount'] = rcount
    namespace['count'] = rcount + count
    namespace['read'] = read[start:end]
    namespace['unread'] = unread

    namespace['rangelist'] = get_rangelist(start, end, count)

    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_message_form(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    sender = kwargs.get('sender', None)
    receiver = kwargs.get('receiver', None)
    POST = kwargs.get('POST', None)

    if ContentType.objects.get_for_model(receiver) == ContentType.objects.get_for_model(Message):
        namespace['reply'] = receiver.description
        namespace['user'] = receiver.sender
    else:
        namespace['reply'] = None
        namespace['user'] = receiver

    if POST and POST.get("form_id") == "pp_message_form":
        form = MessageForm(POST)
        if form.is_valid():
            mes = form.save(commit=False)
            mes.sender = sender
            mes.receiver = namespace['user']
            mes.read = False
            mes.save()
            #raise HttpRedirectException(HttpResponseRedirect(receiver.get_absolute_url()))
            form = MessageForm()
            namespace['complete'] = True
            notification_send.send(sender=mes.sender, obj=mes, reply_to=namespace['reply'])

    else:
        form = MessageForm()

    namespace['form'] = form
    namespace['errors'] = form.errors

    output = nodelist.render(context)
    context.pop()

    return output
