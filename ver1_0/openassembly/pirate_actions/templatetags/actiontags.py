from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.db import transaction
from django.middleware import csrf
from django.contrib.contenttypes.models import ContentType
from pirate_actions.models import Action, ActionForm
from django.contrib.auth.models import User
from django.db.models import Count
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from pirate_core.views import HttpRedirectException, namespace_get

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_action')


@block
def pp_action_form(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    obj = kwargs.get('object', None)
    user = kwargs.get('user', None)
    POST = kwargs.get('POST', None)

    if POST and POST.get("form_id") == "pp_action_form":
        form = ActionForm(POST)
        #if form is valid frab the lat/long from the geolocation service
        if form.is_valid():
            desc = form.cleaned_data['description']
            content_type = ContentType.objects.get_for_model(obj.__class__)
            a = Action(user=user, object_pk=obj.pk, content_type=content_type,
                    description=desc, parent_pk=obj.parent.pk, created_dt=datetime.datetime.now())
            a.save()
    else:
        form = ActionForm()

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_get_actions(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    obj = kwargs.get('object', None)
    page = kwargs.get('page', 1)
    if page is None:
        page = 1

    if obj is not None:
        if isinstance(obj, User):
            actions = Action.objects.filter(user=obj)
        else:
            actions = Action.objects.filter(object_pk=obj.pk)
    else:
        actions = Action.objects.all()

    paginator = Paginator(actions, 10)

    try:
        actions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        actions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        actions = paginator.page(paginator.num_pages)
    except:
        raise

    namespace['actions'] = actions

    output = nodelist.render(context)
    context.pop()

    return output
