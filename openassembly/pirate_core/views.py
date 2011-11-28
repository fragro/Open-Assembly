from exceptions import ValueError
from django.template import RequestContext, loader, add_to_builtins
from django.template import TemplateSyntaxError, TemplateDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404,redirect
from django.test.client import Client
import simplejson
from django.shortcuts import render
from markdown import markdown
from minidetector import detect_mobile


@detect_mobile
def welcome_page(request):
    if request.mobile:
        return HttpResponseRedirect('mobile.html')
    return HttpResponseRedirect('index.html')


def home_page(request):
    from pirate_topics.models import Topic
    topic, is_new = Topic.objects.get_or_create(summary="Tulsa Film Genome Project", description="A collaborative film experiment. First we can collaboratively determine the best places to shoot short scenes in Tulsa. Then we will edit different variations using the scene ideas you have given us, and you can vote on the variation you like most. Then we apply a <a href='http://en.wikipedia.org/wiki/Genetic_algorithm'>genetic algorithm</a> to evolve the best montage using your votes as the natural selection.",parent=Topic.objects.null_dimension())
    content_type = ContentType.objects.get_for_model(topic)
    return HttpResponseRedirect('/issues.html?_t=' + str(content_type.pk) + '&_o=' + str(topic.pk) + '&_s=0&_e=20&_d=hn')


def redirectable(func):
    """
    This decorator provides the functionality required to use form view tags in templates
    in conjunction with arbitrary views, by wrapping those views with a try-catch statement
    that deals with the HttpRedirectException and can return HttpRedirectResponse objects.

    Because most templates will require data included in the request, and this decorator
    is typically used with generic views, it should be used in conjunction with the
    django.core.context_processors.request context processor.

    >>> from django import template
    >>> from pirate_issues.models import Topic
    >>> topic = Topic(text="A test topic.")
    >>> topic.save()

    >>> ts = "{% load pp_url %}{% pp_url template='object_test.html' object=topic %}"
    >>> url = template.Template(ts).render(template.Context({'topic':topic}))

    >>> from django.test.client import Client
    >>> c = Client()
    >>> response = c.get(url)
    >>> response.content[:12]
    'A test topic'
    """

    def view(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        #this case occurs when in development mode
        except TemplateSyntaxError, e:
            if hasattr(e, 'exc_info') and e.exc_info[0] is HttpRedirectException:
                return e.exc_info[1].http_response_redirect
            else:
                raise

        #this happens in production
        except HttpRedirectException, e:
            return e.http_response_redirect

    view.__doc__ = func.__doc__
    return view


class HttpRedirectException(Exception):
    '''
    This exception is used by low-level tags execting inside the django template
    rendering engine to transfer control directly and immediately back to the
    generic view, in order to cause a redirect instruction to be returned.  This
    is intended to be used by tags that process forms.
    '''
    def __init__(self, http_response_redirect):
        if isinstance(http_response_redirect, basestring):
            http_response_redirect = HttpResponseRedirect(http_response_redirect)

        elif not isinstance(http_response_redirect, HttpResponseRedirect):
            raise ValueError("The only valid argument to this constructor is " + 
                             "HttpResponseRedirect")
        self.http_response_redirect = http_response_redirect

    def __repr__(self):
        return "HttpRedirectException(http_response_redirect=" + \
                                     "self.http_response_redirect.__repr__())"


def namespace_get(namespace_str):
    '''
    This function takes advantage of closure on the namespace_str to produce a namespace
    retrieval/creation function that can be reused by many different pp modules.  Without
    this, the same eight lines of code would be duplicated across all of the modules, and
    even inside each tag function.

    Note: in order to avoid conflicts or overwriting objects from outside the scope of any
    block, be sure to make your call to your local instance of get_namespace AFTER invoking
    context.push().
    '''

    def get_namespace(context):
        # first, grab the namespace if it is there, or if it not, create it
        if namespace_str in context:
            ret_val = context[namespace_str].copy()
        else:
            ret_val = {}

        context[namespace_str] = ret_val
        return ret_val

    return get_namespace
