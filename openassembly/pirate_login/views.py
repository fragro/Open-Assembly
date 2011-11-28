# Create your views here.
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from pirate_core import HttpRedirectException, namespace_get, FormMixin

def logout_view(request):
    try:goto = request.session['currently_visiting']
    except: goto = '/index.html'
    logout(request)
    return HttpResponseRedirect(goto)
