from django import template
from django import forms
from django.http import HttpResponseRedirect
import datetime
from django.contrib.contenttypes.models import ContentType
from pirate_deliberation.models import Argument, Stance, get_argument_list
from pirate_consensus.models import Consensus, UpDownVote
from pirate_reputation.models import ReputationDimension
from pirate_core.helpers import clean_html
from pirate_deliberation.forms import YeaArgumentForm, NayArgumentForm
from pirate_deliberation.choices import ARG_TYPES_DICT

from pirate_core import HttpRedirectException, namespace_get, FormMixin

from pirate_signals.models import aso_rep_event,notification_send, relationship_event

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_argumentation')


@block
def pp_get_argument_count(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    obj = kwargs.pop('object', None)
    arg_type = kwargs.pop('arg_type', None)

    arg_list = Argument.objects.all()

    if isinstance(arg_type, unicode):
        arg_type, created = Stance.objects.get_or_create(arg=arg_type)
    if obj:
        arg_list = arg_list.filter(parent_pk=obj.id)
    if arg_type:
        arg_list = arg_list.filter(stance=arg_type)
    namespace['count'] = arg_list.count()

    output = nodelist.render(context)
    context.pop()
    return output


@block
def pp_get_arg_types(context, nodelist, *args, **kwargs):
    """This block tag grabs all available Stances.

    Can be used in the following manner:
    {% pp_get_arg_types %}
       Do stuff with {{ pp_blob.arg_type_list }}
    {% endpp_get_arg_types %}"""

    context.push()
    namespace = get_namespace(context)

    arg_type_list = Stance.objects.all()
    namespace['arg_type_list'] = arg_type_list


    output = nodelist.render(context)
    context.pop()
    return output

@block
def pp_get_argument_list(context, nodelist, *args, **kwargs):
    """This block tag grabs a list of arguments, based on the issue
    that is paseed into the context and then places the lsit of arguments
    into the context.
    
    Can be used in the following manner:
    {% pp_get_argument_list solution=solution rng=request.rng %}
       Do stuff with {{ pp_argumentation.argument_list }}
    {% endpp_get_argument_list %}
    """
    #TODO:Split argument list into list of argument lists by Stance  
    context.push()
    namespace = get_namespace(context)

    obj = kwargs.pop('object', None)
    arg_type = kwargs.pop('arg_type', None)
    start = kwargs.pop('start', None)
    end = kwargs.pop('end', None)

    arg_list = get_argument_list(obj, arg_type, start, end)

    namespace['argument_list'] = arg_list
    output = nodelist.render(context)
    context.pop()
    return output


@block
def pp_argument_form(context, nodelist, *args, **kwargs):
    '''
    This block tag can create or process forms either to create or to modify arguments.
    Usage is as follows:

    {% pp_argument_form POST=request.POST path=request.path object=pp-issue.issue arg = pp_argumentation.argument%}
       Do stuff with {{ pp_argumentation.form }}.
    {% endpp_argument_form %}
    '''

    context.push()
    namespace = get_namespace(context)

    POST = kwargs.get('POST', None)
    obj = kwargs.get('object', None)
    arg_type = kwargs.get('dimension', None)
    user = kwargs.get('user', None)

    #arg_type = ARG_TYPES_DICT[arg_type]
    #stance, created = Stance.objects.get_or_create(arg=arg_type)

    if isinstance(obj, Argument):
        arg = obj
        parent = arg.parent
    else:
        arg, parent = (None, obj)

    if POST and user != None:
        if POST.get("form_id") == "pp_argument_form_nay":
            stance, created = Stance.objects.get_or_create(arg='nay')
            form = NayArgumentForm(POST)
        if POST.get("form_id") == "pp_argument_form_yea":
            stance, created = Stance.objects.get_or_create(arg='yea')
            form = YeaArgumentForm(POST)
        if form.is_valid():
            new_arg = form.save(commit=False)
            new_arg.stance = stance
            new_arg.user = user
            new_arg.parent_type = ContentType.objects.get_for_model(parent)
            new_arg.parent_pk = parent.id
            new_arg.save()
            namespace['object_pk'] = new_arg.pk
            namespace['content_type'] = ContentType.objects.get_for_model(new_arg).pk
            cons, is_new = Consensus.objects.get_or_create(content_type=ContentType.objects.get_for_model(Argument),
                                                           object_pk=new_arg.pk, parent_pk=new_arg.parent_pk)

            if is_new:
                cons.intiate_vote_distributions()
                #if this is a new issue/consensus, send signal for reputation
                aso_rep_event.send(sender=new_arg, event_score=4, user=new_arg.user, initiator=new_arg.user, dimension=ReputationDimension.objects.get('Argument'), related_object=new_arg)
                notification_send.send(sender=new_arg.user, obj=new_arg, reply_to=parent)
                relationship_event.send(sender=new_arg.user, obj=new_arg, parent=parent)

            #raise HttpRedirectException(HttpResponseRedirect(new_arg.get_absolute_url()))
            if arg_type == 'n':
                form = NayArgumentForm()
            if arg_type == 'y':
                form = YeaArgumentForm()
        else:
            namespace['errors'] = form.errors
    else:
        if arg_type == 'n':
            form = NayArgumentForm()
        if arg_type == 'y':
            form = YeaArgumentForm()

    namespace['help_text'] = 'Supply a ' + str(arg_type) + ' Argument for your position.'
    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()
    return output
