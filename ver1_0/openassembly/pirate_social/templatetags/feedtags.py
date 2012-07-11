from django import template
from django import forms
from django.http import HttpResponseRedirect

from pirate_social.models import Subscription,RelationshipEvent

from pirate_core.views import HttpRedirectException, namespace_get

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_feed')

@block
def pp_get_feed(context, nodelist, *args, **kwargs):
    
    """
    This function get's recent feeds from a user's Subscriptions, with minimal
    unnecessary database calls. This function could be further optimized however.
    {% pp_get_feed user=request.user %}
        {% for f in pp_feed.feed %}
            {{f}}
        {% endfor %}
    {% endpp_get_feed %}"""
    
    context.push()
    namespace = get_namespace(context)

    user = kwargs.pop('user', None)
    subs = Subscription.objects.all()
    subs = subs.filter(subscriber=user)
    eval_str = ""
    
    
    """To facilitate feeds, we have to use a bit of eval() trickery. 
        The string 'eval_str' consists of a series of OR operations
        on relationship events, that allow the system to filter out 
        all relationship events where the initiator is in the list
        of subscriptions."""
    #TODO: in the future we need to filter this list on specific types
    #       of content, so that we don't needlessly return objs such as tagging
    #       for the generic feed, but still allow for tagging for specific activity viewing
    query_dict = {}
    for s in subs:
        u = s.subscribee
        rels = RelationshipEvent.objects.all()
        rels = rels.filter(initiator=u)
        query_dict[u.id] = rels
        eval_str += "query_dict[" + str(u.id) + "] | "
    if eval_str != "":
        master_query = eval(eval_str[:len(eval_str)-2])
        master_query = master_query.order_by('-created_on')   
    else: master_query = []    
        
    namespace['feed'] = master_query
    output = nodelist.render(context)
    context.pop()

    return output
