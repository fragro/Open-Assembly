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

get_namespace = namespace_get('pp_social')

@block
def pp_get_all_users(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    users = User.objects.all()
    
    
    
    namespace['feed'] = master_query
    output = nodelist.render(context)
    context.pop()

    return output
