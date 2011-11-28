from django import template
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from pirate_core import HttpRedirectException, namespace_get, FormMixin

from pirate_permissions.models import Permission

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

'''
This file contains all of the tags that pertain to Issue objects, in order to fetch one
issue, a list of issues, or to add or update an issue.
'''

# this function assignment lets us reuse the same code block a bunch of places
get_namespace = namespace_get('pp_permissions')


@block
def cani(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    # this tag only works if a valid pair is assigned to the 'object=' argument
    obj = kwargs.pop('object', None)
    user = kwargs.pop('user', None)

    if obj is None:
        raise ValueError("tag requires that a object pair be passed "
                             "to it assigned to the 'object=' argument, and that the str "
                             "be assigned the string value 'issue'.")

    try:
        perm = Permission.objects.get(user=user, object_pk=obj.pk)
        namespace['permission'] = True
    except:
        namespace['permission'] = False

    namespace['issue'] = obj

    output = nodelist.render(context)
    context.pop()

    return output
