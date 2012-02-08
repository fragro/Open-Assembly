from django import template
from django import forms
from django.http import HttpResponseRedirect
import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from pirate_core import HttpRedirectException, namespace_get, FormMixin
from pirate_social.models import Subscription

from pirate_signals.models import aso_rep_event, notification_send

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_subscription')


@block
def pp_get_subscribees_for_user(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    user = kwargs.pop('user', None)
    start = kwargs.get('start', None)
    end = kwargs.get('end', None)

    if start is None and end is None:
        start = 0
        end = 8
    else:
        try:
            start = int(start)
            end = int(end)
        except:
            raise ValueError('start and end values must be ints')

    if user is None:
        raise ValueError("pp_subscription_form tag requires that a User object be passed "
                             "to it assigned to the 'user=' argument")

    subs = Subscription.objects.all()
    subs = subs.filter(subscriber=user)
    count = subs.count()

    namespace['subscribees'] = subs[start:end]
    namespace['count'] = count
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_get_subscribers_for_user(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    user = kwargs.pop('user', None)
    start = kwargs.get('start', None)
    end = kwargs.get('end', None)

    if start is None and end is None:
        start = 0
        end = 8
    else:
        try:
            start = int(start)
            end = int(end)
        except:
            raise ValueError('start and end values must be ints')
    if user is None:
        raise ValueError("pp_subscription_form tag requires that a User object be passed "
                             "to it assigned to the 'user=' argument")

    subs = Subscription.objects.all()
    subs = subs.filter(subscribee=user)
    count = subs.count()

    namespace['subscribers'] = subs[start:end]
    namespace['count'] = count
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_subscriber_count(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    user = kwargs.pop('user', None)
    if user is None:
        raise ValueError("pp_subscription_form tag requires that a User object be passed "
                             "to it assigned to the 'user=' argument")

    subs = Subscription.objects.all()
    subs = subs.filter(subscribee=user)
    count = subs.count()

    namespace['count'] = count
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_subscribee_count(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    user = kwargs.pop('user', None)
    if user is None:
        raise ValueError("pp_subscription_form tag requires that a User object be passed "
                             "to it assigned to the 'user=' argument")

    subs = Subscription.objects.all()
    subs = subs.filter(subscriber=user)
    count = subs.count()

    namespace['count'] = count
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_has_subscription(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    # this tag only works if a valid pair is assigned to the 'object=' argument
    POST = kwargs.get('POST', None)
    subscriber = kwargs.pop('subscriber', None)
    subscribee = kwargs.pop('subscribee', None)
    if subscriber is None:
        raise ValueError("pp_subscription_form tag requires that a object be passed "
                             "to it assigned to the 'subscriber=' argument")
    if subscribee is None:
        raise ValueError("pp_subscription_form tag requires that a object be passed "
                             "to it assigned to the 'subscribee=' argument")

    try:
        Subscription.objects.get(subscriber=subscriber, subscribee=subscribee)
        namespace['has_subscription'] = True
    except:
        namespace['has_subscription'] = False

    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_end_subscription_form(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    # this tag only works if a valid pair is assigned to the 'object=' argument
    POST = kwargs.get('POST', None)
    subscriber = kwargs.pop('subscriber', None)
    subscribee = kwargs.pop('subscribee', None)
    if subscriber is None:
        raise ValueError("pp_subscription_form tag requires that a object be passed "
                             "to it assigned to the 'subscriber=' argument")
    if subscribee is None:
        raise ValueError("pp_subscription_form tag requires that a object be passed "
                             "to it assigned to the 'subscribee=' argument")
                             
                             
    if POST and POST.get("form_id") == "pp_subscription_form":
        form = SubscriptionForm(POST)
        if form.is_valid():   
            sub = Subscription.objects.get(subscriber=subscriber,subscribee=subscribee)
            sub.delete()
            c_type = ContentType.objects.get_for_model(subscribee)
            raise HttpRedirectException(HttpResponseRedirect("/user_profile.html?_t=" + str(c_type.pk) + "&_o=" + str(subscribee.pk)))
    else: form = SubscriptionForm()
    
    if subscriber != subscribee: namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output
        

@block
def pp_subscription_form(context, nodelist, *args, **kwargs):
    
    context.push()
    namespace = get_namespace(context)

    # this tag only works if a valid pair is assigned to the 'object=' argument
    POST  = kwargs.get('POST', None)
    subscriber = kwargs.pop('subscriber', None)
    subscribee = kwargs.pop('subscribee', None)
    if subscriber is None:
        raise ValueError("pp_subscription_form tag requires that a object be passed "
                             "to it assigned to the 'subscriber=' argument")
    if subscribee is None:
        raise ValueError("pp_subscription_form tag requires that a object be passed "
                             "to it assigned to the 'subscribee=' argument")
                             
                             
    if POST and POST.get("form_id") == "pp_subscription_form":
        form = SubscriptionForm(POST)
        if form.is_valid():   
            sub = Subscription(subscriber=subscriber,subscribee=subscribee,created_dt=datetime.datetime.now())
            sub.save()
            c_type = ContentType.objects.get_for_model(subscribee)
            raise HttpRedirectException(HttpResponseRedirect("/user_profile.html?_t=" + str(c_type.pk) + "&_o=" + str(subscribee.pk)))
    else: form = SubscriptionForm()
    
    if subscriber != subscribee: namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output
    
class SubscriptionForm(forms.ModelForm):
    """This form is used to create a subscription object between two users."""

    class Meta:
        model = Subscription
        exclude = ('subscriber','subscribee')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_subscription_form")
    
