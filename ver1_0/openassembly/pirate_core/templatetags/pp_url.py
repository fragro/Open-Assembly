from exceptions import ValueError

from django import template
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
import string


from customtags.decorators import function_decorator
register = template.Library()
function = function_decorator(register)

from pirate_core.middleware import TYPE_KEY, OBJ_KEY, CTYPE_KEY, STR_KEY, PHASE_KEY
from pirate_core.middleware import START_KEY, END_KEY, DIM_KEY, SCROLL_KEY, RETURN_KEY, SIMPLEBOX_KEY
from pirate_forum.models import get_pretty_url

'''
This file contains the tag responsible for creating useful urls within pp templates.
'''
#quick hack until I push this to the oa_cache admin interface
TEMPLATE_DICT = {'/user_profile.html': '/p/user', '/None': '/?hash=#', '/issues.html': '/p/list',
                    '/topics.html': '/p/topics', '/faq.html': '/p/faq',
                    '/200.html': '/p/200', '/detail.html': '/p/item',
                    '/submit.html': '/p/submit', '/arpv.html': '/p/arpv', '/register.html': '/p/register'}


@function
def pp_url(*args, **kwargs):
    """
    This block tag will produce a url that will link to the designated view or pattern
    name, and then will optionally populate the request passed to that view with
    either a specific ORM object, or a numerical range (start...end), as long as
    the pirate_core.url_middleware.UrlMiddleware is included in the projects'
    MIDDLEWARE_CLASSES. Any kwargs included in addition to "view", "object", "start"
    and "end" will be passed to redirect in order to produce the url for the designated
    view.

    The default value for "view" is "pp-page", which expects that the kwarg "template" be
    included, passing in the name of the template being linked to.

    For example:

    {% pp_url object=object template="filename.html" %}

    {% pp_url template="filename.html" start=0 end=30 dimension="n" %}

    {% pp_url template="filename.html" %}

    >>> from django import template
    >>> from pirate_topics.models import Topic
    >>> topic = Topic(summary="A test topic.", shortname="test-topic", description="test", group_members=0)
    >>> topic.save()
    >>> load = "{% load pp_url %}"

    >>> ts = "{% pp_url template='example.html' object=topic %}"
    >>> template.Template(load + ts).render(template.Context({'topic':topic}))
    u'/p/example/k-test-topic'

    >>> ts = "{% pp_url template='example.html' object=topic start=0 end=30 %}"
    >>> template.Template(load + ts).render(template.Context({'topic':topic}))
    u'/p/example/k-test-topic/s-0/e-30'

    >>> ts = "{% pp_url template='example.html' start=0 end=30 dimension='new' %}"
    >>> template.Template(load + ts).render(template.Context({'topic':topic}))
    u'/p/example/s-0/e-30/d-new'

    >>> topic.delete()

    >>> topic.delete()
    """
    obj = kwargs.pop('object', None)
    start = kwargs.pop('start', None)
    end = kwargs.pop('end', None)
    dimension = kwargs.pop('dimension', None)
    #argument for javascript scroll_to function
    scroll_to = kwargs.pop('scroll_to', None)
    return_path = kwargs.pop('return_path', None)
    panel = kwargs.pop('panel', None)
    return_query = kwargs.pop('return_query', None)
    htmlsafe = kwargs.pop('htmlsafe', None)
    #need to change ampersand for facebook edge case
    simplebox = kwargs.pop('simplebox', None)
    #for keeping simplbox open
    sort_type = kwargs.pop('sort_type', None)
    phase_key = kwargs.pop('phase', None)

    pattern = kwargs.pop('view', 'pp-page')

    if (start is None and end is not None) or (start is not None and end is None):
        raise ValueError("If either the 'start' or 'end' argument is specified, then "
                         "both should be specified.")

    if obj is not None:
        if isinstance(obj, models.Model):
            content_type = ContentType.objects.get_for_model(obj.__class__)
            rev_kwargs = {'content_type_id': content_type.pk,
                           'obj_id': str(obj.pk)}

        else:
            raise ValueError("If 'object' argument is specified, it must be of type "
                             "django.models.Model. Specified object is of type '%s.'"
                             % obj.__class__.__name__)
        if htmlsafe is not None:
            rev_kwargs['htmlsafe'] = True

        if scroll_to is not None:
            rev_kwargs['scroll_to'] = scroll_to

        if sort_type is not None:
            rev_kwargs['sort_type'] = sort_type

        if start is not None and end is not None:
            rev_kwargs['start'] = start
            rev_kwargs['end'] = end
        if simplebox is not None:
            rev_kwargs['simplebox'] = True
        if phase_key is not None:
            rev_kwargs['phase'] = phase_key

        if dimension is not None:
            output = get_reverse(pattern, kwargs, dimension=dimension, **rev_kwargs)
        else:
            output = get_reverse(pattern,  kwargs, **rev_kwargs)
    else:
        rev_kwargs = {}
        if start is not None and end is not None:
            rev_kwargs['start'] = start
            rev_kwargs['end'] = end
        if simplebox is not None:
            rev_kwargs['simplebox'] = True
        if dimension is not None:
            rev_kwargs['dimension'] = dimension
        if return_path is not None and return_query:
            rev_kwargs['returnurl'] = return_path + '?' + return_query
        output = get_reverse(pattern, kwargs, **rev_kwargs)

    #need to append reverse of pattern to user's recently visited list
    return output


def get_reverse(pattern, kwargs, content_type_id=None,
    obj_id=None, start=None, end=None, dimension=None, scroll_to=None,
    returnurl=None, htmlsafe=None, simplebox=None, is_hash=True, sort_type=None, phase=None):
    try:
        val = reverse(pattern, kwargs=kwargs)
        if val in TEMPLATE_DICT:
            url = TEMPLATE_DICT[val]
        else:
            url = '/p/' + str(val[1:-5])
        inter = ''
        j = '/'
        qu = '/'
    except:
        url = reverse(pattern, kwargs=kwargs)
        inter = '='
        j = '&'
        qu = '?'
    qs = []
    if simplebox is not None:
        qs.append(SIMPLEBOX_KEY + "=s")
    if content_type_id is not None and obj_id is not None:
        #let's make the object part of the url pretty
        obj_str = get_pretty_url(content_type_id, obj_id)
        qs.append(STR_KEY + inter + obj_str)
        #qs.append(TYPE_KEY + inter + str(content_type_id))
        #qs.append(OBJ_KEY + inter + str(obj_id))
    if start is not None and end is not None:
        qs.append(START_KEY + inter + str(start))
        qs.append(END_KEY + inter + str(end))
    if dimension is not None:
        qs.append(DIM_KEY + inter + str(dimension))
    if sort_type is not None:
        qs.append(CTYPE_KEY + inter + str(sort_type))
    if phase is not None:
        qs.append(PHASE_KEY + inter + str(phase))
    if len(qs) > 0:
        qs = qu + j.join(qs)
    else:
        qs = ''
    if htmlsafe is not None:
        qs = qs.replace("&", "%26")
    #last because we use hashes now
    if scroll_to is not None:
        qs += '#' + str(scroll_to)
    if url == "/None":
        url = '/'
    return url + qs
