from django import template

from pirate_core import namespace_get
from settings import DOMAIN
from oa_cache.views import get_cache_or_render, get_object_or_none
from oa_cache.models import interpret_hash
from pirate_forum.models import get_pretty_url, reverse_pretty_url

from BeautifulSoup import BeautifulSoup

import string, re

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

    hashed = request.META['PATH_INFO']

    #we only consider certain items to be

    if string.find(hashed, '.html') == -1 and hashed[0:2] == '/p' or hashed == '/':
        if hashed is None:
            hashed = ''
        if hashed == '/' or hashed == '':
            hashed = '/p/landing'
            #need to make this some sort of home feed for user
        props = get_cache_or_render(request.user, hashed, False, request=request, forcerender=True)

        #get object for the cache
        key, rtype, paramdict = interpret_hash(hashed)
        obj = None
        if 'STR_KEY' in paramdict:
            ctype_pk, obj_pk = reverse_pretty_url(paramdict['STR_KEY'])
            obj = get_object_or_none(ctype_pk, obj_pk)
        elif 'OBJ_KEY' and 'TYPE_KEY' in paramdict:
            ctype_pk = paramdict['TYPE_KEY']
            obj_pk = paramdict['OBJ_KEY']
            obj = get_object_or_none(ctype_pk, obj_pk)

        soup = BeautifulSoup()
        ret = {}
        #need to iterate through the list and build the html with the corresponding divs and html content, requires magic
        for data in props['rendered_list']:
            if data['div'] == '#content':
                soup.feed(data['html'])
            else:
                txt_list = soup.findAll('span', {'id': re.compile(data['div'][1:])})
                txt_list.extend(soup.findAll('div', {'id': re.compile(data['div'][1:])}))
                txt_list.extend(soup.findAll('td', {'id': re.compile(data['div'][1:])}))
                for txt in txt_list:
                    txt.insert(0, data['html'])
                if len(txt_list) == 0:
                    #raise ValueError(data['div'][1:] + soup.prettify())
                    ret[data['div'][1:]] = data['html']
        ret['content'] = soup.prettify()

        namespace['data'] = ret
        namespace['object'] = obj
        namespace['rendered_list'] = None
    namespace['nojs'] = True

    output = nodelist.render(context)
    context.pop()

    return output
