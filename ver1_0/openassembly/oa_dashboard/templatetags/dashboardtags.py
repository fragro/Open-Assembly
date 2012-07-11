from django import template
from pirate_core import namespace_get
from oa_dashboard.models import DashboardPanel
from oa_cache.views import render_hashed
from oa_cache.models import interpret_hash
from django.contrib.auth.models import User
from customtags.decorators import block_decorator


register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('oa_dashboard')


@block
def oa_get_dashboard(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    request = kwargs.get('request', None)
    user = kwargs.get('user', None)
    dashboard_id = kwargs.get('dashboard_id', None)
    boards = []
    namespace['boards'] = {}
    if user is not None and user.is_authenticated() and dashboard_id is not None:
        #get platform for this contenttype and user
        boards = DashboardPanel.objects.filter(user=user,
                dashboard_id=dashboard_id).order_by('priority')
    elif not user.is_authenticated():
        try:
            us = User.objects.get(username='congress_critter')
            boards = DashboardPanel.objects.filter(user=us,
                dashboard_id=dashboard_id).order_by('priority')
        except:
            pass
        #for each board, render the respective information
    dash = []
    for board in boards:
        key, rendertype, paramdict = interpret_hash(board.plank)
        #add start and end information for pagination
        plank = board.plank + '/s-0/e-20'
        renderdict = render_hashed(request, plank, user, extracontext={'dashobj': board, 'TYPE': 'HTML', 'start': 0, 'end': 20})
        if 'DIM_KEY' in paramdict:
            dim = paramdict['DIM_KEY']
        else:
            dim = ''
        print board
        #if there is a total count for a list in this we need to add that so that the dash renders it might fine
        if renderdict['rendertype'] in renderdict['counts']:
            count = renderdict['counts'][renderdict['rendertype']]
        else:
            count = None
        dash.append((renderdict['renders'], renderdict['object'], board, renderdict['rendertype'], dim, 0, 20, count))
    namespace['boards'] = dash
    output = nodelist.render(context)
    context.pop()

    return output


@block
def oa_has_dash(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)

    if user is not None and user.is_authenticated():
        #get platform for this contenttype and user
        boards = DashboardPanel.objects.filter(user=user)
        if boards.count() > 0:
            namespace['has_board'] = True
        else:
            namespace['has_board'] = False
    output = nodelist.render(context)
    context.pop()

    return output
