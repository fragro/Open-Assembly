# Create your views here.
from django.contrib.auth import logout
from django.shortcuts import redirect


def logout_view(request):
    if request.user.is_authenticated() and request.user.is_active:
        logout(request)
	return redirect('/')

