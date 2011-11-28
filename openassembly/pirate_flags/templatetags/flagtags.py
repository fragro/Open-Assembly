from pirate_flags.forms import FlagForm
from pirate_flags.models import Flag,UserFlag
from django import template
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from pirate_consensus.models import Consensus

from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from pirate_core.views import HttpRedirectException, namespace_get
from pirate_signals.models import aso_rep_event
from pirate_reputation.models import ReputationDimension

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_flag')

@block
def pp_flag_form(context, nodelist, *args, **kwargs): 

    context.push()
    namespace = get_namespace(context)

    obj = kwargs.pop('object', None)
    POST = kwargs.pop('POST', None)
    user = kwargs.get('user', None)
    PI = kwargs.get('PATH_INFO',None)
    QS = kwargs.get('QUERY_STRING',None)
    path = PI + '?' + QS
    
    if POST is not None and POST.get("form_id") == "pp_flag_form":

        form = FlagForm(POST)
        if form.is_valid():
            flag = form.cleaned_data['flag']
            consensus = Consensus.objects.get(object_pk=obj.pk)
            flag, created = Flag.objects.get_or_create(parent_pk=consensus.pk, flag_type=flag, content_type=consensus.content_type, object_pk=obj.pk)
            
            uflag, new = UserFlag.objects.get_or_create(user=user,flag=flag,mode=True)
            if new: #if this user hasn't voted on this flag before
                flag.votes+=1
                flag.counter=0
                flag.save()
            aso_rep_event.send(sender=user, event_score=1, user=flag.content_object.user, initiator=user, dimension=ReputationDimension.objects.get('Flag'),related_object=consensus)

            uflag.save()
            
            raise HttpRedirectException(HttpResponseRedirect(path))
    else:   
        form = FlagForm()
        
    namespace['form'] = form

        
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_get_flags(context, nodelist, *args, **kwargs): 
    """
    Populates the context with a SpectrumForm, allowing users to select what
    voting type is applied to the object or the objects children.
    
    Unless the number of related objects is limited, for example solutions to 
    a problem, plurality voting is required. As the number of objects considered
    for voting increases, it becomes increasingly impossible to rank or apply 
    weighted voting to the entire set.
    """
    context.push()
    namespace = get_namespace(context)

    obj = kwargs.pop('object', None)
    user = kwargs.pop('user', None)
    
    flags = Flag.objects.filter(object_pk=obj.pk)
    
    if user.is_authenticated(): 
        ret_flags = []
    
        for flag in flags:
            try:
                uflag = UserFlag.objects.get(user=user,flag=flag)
                if uflag.mode == True:
                    up_img = 'acti'
                    down_img = 'flat'
                elif uflag.mode == False:
                    up_img = 'flat'
                    down_img = 'acti'
            except:
                up_img = 'flat'
                down_img = 'flat'
            ret_flags.append((flag,up_img,down_img))
    else: ret_flags = [(f, 'flat', 'flat') for f in flags]

    namespace['flags'] = ret_flags

        
    output = nodelist.render(context)
    context.pop()

    return output
