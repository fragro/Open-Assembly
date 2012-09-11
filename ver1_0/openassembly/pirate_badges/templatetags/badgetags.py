from django import template
from django import forms
from django.http import HttpResponseRedirect
import datetime
from django.contrib.auth.models import User
from pirate_badges.models import Badge, BadgeDimension, test_badge, BadgeType
from pirate_core import HttpRedirectException, namespace_get, FormMixin
from pirate_social.models import RelationshipEvent 
from pirate_deliberation.models import Argument
from pirate_consensus.models import UpDownVote
from django.contrib.contenttypes.models import ContentType
from tagging.models import TaggedItem

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_badge')


@block
def pp_badge_dimensions(context, nodelist, *args, **kwargs):
    '''Retrieves all dimensions of badges'''
    context.push()
    namespace = get_namespace(context)

    namespace['badges'] = BadgeDimension.objects.all()

    output = nodelist.render(context)
    context.pop()
    return output


@block
def pp_get_badges(context, nodelist, *args, **kwargs):
    '''
    This block tag can create or process forms to get badges.
    Usage is as follows:

    {% pp_get_badges user=request.object %}
       Do stuff with {{ pp_badge.badges }}.
    {% endpp_get_badges %}
    '''

    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    if user is not None:
        badges = Badge.objects.filter(user=user)
        total = badges.count()
        for val in BadgeType.objects.all():
            testbadges = badges.filter(badge_type_id=val.id)
            try:
                namespace[val.name] += testbadges.count()
            except:
                namespace[val.name] = testbadges.count()
        namespace['total'] = total
        namespace['badges'] = badges
    else:
        raise ValueError("Must supply 'user' argument to pp_get_badges")

    output = nodelist.render(context)
    context.pop()
    return output


@block
def pp_check_badges(context, nodelist, *args, **kwargs):
    '''
    This block tag can create or process forms to see if there are new badges.
    Usage is as follows:

    {% pp_check_badges user=request.object %}
       Do stuff with {{ pp_badge.new_badges }}.
    {% endpp_check_badges %}
    '''

    context.push()
    namespace = get_namespace(context)

    namespace['new_badges'] = new_badges

    output = nodelist.render(context)
    context.pop()
    return output 

"""Checks if badge is given yet, if new adds to new_badge list"""
def check_add_badge(existing_badges, new_badges, verbose_name, name, badge_type, check):
        if name in existing_badges or not check: return new_badges
        badge_type = BadgeDimension.objects.get(verbose_name=verbose_name, name=name,badge_type=badge_type)
        user_badge, is_new = Badge.objects.get_or_create(dimension=badge_type,user=user, badge_type=badge_type)
        new_badges.append(user_badge)
        return new_badges

