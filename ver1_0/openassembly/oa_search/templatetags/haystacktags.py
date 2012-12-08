from django import template
from pirate_core import HttpRedirectException, namespace_get

from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from haystack.forms import ModelSearchForm, FacetedSearchForm
from haystack.query import EmptySearchQuerySet

RESULTS_PER_PAGE = getattr(settings, 'HAYSTACK_SEARCH_RESULTS_PER_PAGE', 20)

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

# this function assignment lets us reuse the same code block a bunch of places
get_namespace = namespace_get('oa_search')

"""
Port of the Haystack Search View to our TemplateTag language
"""


@block
def oa_haystack_search(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    dimension = kwargs.get('search_key', None)
    POST = kwargs.get('POST', None)
    page = kwargs.get('page', None)
    if page is None:
        page = 1

    load_all = True
    form_class = ModelSearchForm
    searchqueryset = None
    results_per_page = None

    query = ''
    results = EmptySearchQuerySet()

    if dimension is not None:
        query = dimension
        form = form_class({'q': dimension}, searchqueryset=searchqueryset, load_all=load_all)
        results = form.search()
    elif POST is not None:
        form = form_class(POST, searchqueryset=searchqueryset, load_all=load_all)
        if form.is_valid():
            query = form.cleaned_data['q']
            results = form.search()
    elif query == '':
        form = form_class(searchqueryset=searchqueryset, load_all=load_all)

    paginator = Paginator(results, results_per_page or RESULTS_PER_PAGE)

    try:
        page = paginator.page(page)
    except InvalidPage:
        namespace['error'] = "No Such Page of Results"

    namespace['form'] = form
    namespace['page'] = page
    namespace['paginator'] = paginator
    namespace['query'] = query

    if getattr(settings, 'HAYSTACK_INCLUDE_SPELLING', False):
        namespace['suggestion'] = form.get_suggestion()
    else:
        namespace['suggestion'] = None

    output = nodelist.render(context)
    context.pop()

    return output
