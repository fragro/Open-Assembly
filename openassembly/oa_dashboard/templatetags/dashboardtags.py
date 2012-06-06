from django import template
from oa_platform.models import Platform, PlatformDimension
from pirate_core import namespace_get
from django.contrib.contenttypes.models import ContentType
from oa_dashboard.models import DashboardPanel
from oa_cache.views import render_hashed

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

    namespace['boards'] = {}
    if user is not None and user.is_authenticated() and dashboard_id is not None:
        #get platform for this contenttype and user
        boards = DashboardPanel.objects.filter(user=user,
                dashboard_id=dashboard_id).order_by('priority')
        #for each board, render the respective information
        dash = []
        for board in boards:
            ret, obj, rtype = render_hashed(request, board.plank, user, extracontext={'dashobj': board, 'TYPE': 'HTML'})
            print board
            dash.append((ret, obj, board, rtype))
        namespace['boards'] = dash
    output = nodelist.render(context)
    context.pop()

    return output
