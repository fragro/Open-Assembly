from django import template

from pirate_core import namespace_get
from oa_cache.views import render_hashed

from settings import DEBUG, DOMAIN

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_cache')


@block
def pp_get_cached_data(context, nodelist, *args, **kwargs):
    '''
    Returns a ForumDimension object with key=dimension
    '''
    context.push()
    namespace = get_namespace(context)

    request = kwargs.get('request', None)

    ret, obj, rtype = render_hashed(request, None, None, extracontext={'TYPE': 'HTML'})

    namespace['rendertype'] = rtype
    namespace['data'] = ret
    namespace['DOMAIN'] = DOMAIN
    namespace['object'] = obj
    namespace['rendered_list'] = None

    namespace['nojs'] = True
    output = nodelist.render(context)
    context.pop()

    return output
