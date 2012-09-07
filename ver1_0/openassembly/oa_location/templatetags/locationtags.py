from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.db import transaction
from django.middleware import csrf
from django.contrib.contenttypes.models import ContentType
from oa_location.models import LocationForm, Place

from geopy import geocoders 

from pirate_core.views import HttpRedirectException, namespace_get

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('oa_loc')


@block
def oa_location_form(context, nodelist, *args, **kwargs):

	context.push()
	namespace = get_namespace(context)

	obj = kwargs.get('object', None)
	user = kwargs.get('user', None)
	POST = kwargs.get('POST', None)
	start = kwargs.get('start', 0)
	end = kwargs.get('end', 5)
	

	if POST and POST.get("form_id") == "oa_location_form":
		form = LocationForm(POST)
		#if form is valid frab the lat/long from the geolocation service
		if form.is_valid():
			gn = geocoders.Google() 
			loc = list(gn.geocode(form.cleaned_data['description'], exactly_one=False))
			loc = [(i[0], i[1][0], i[1][1]) for i in loc[start:end]]
			namespace['location'] = loc

	else:
		form = LocationForm()

	namespace['form'] = form
	output = nodelist.render(context)
	context.pop()

	return output


@block
def oa_location_get(context, nodelist, *args, **kwargs):

	context.push()
	namespace = get_namespace(context)

	obj = kwargs.get('object', None)
	ctype = kwargs.get('content_type', None)

	#pass in a contenttype id
	try:
		ctype = ContentType.objects.get(name=ctype)
	except:
		ctype = None

	if obj is not None and obj != 'location':
		places = Place.objects.filter(object_pk=obj.pk)

		if len(places) == 0:
			namespace['places'] = places[0]

	elif ctype is not None:
		places = Place.objects.filter(content_type=ctype)
		namespace['places'] = places

	else:
		places = Place.objects.all()
		namespace['places'] = places

	output = nodelist.render(context)
	context.pop()

	return output