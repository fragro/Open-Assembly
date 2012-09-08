from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.db import transaction
from django.middleware import csrf
from django.contrib.contenttypes.models import ContentType
from oa_location.models import LocationForm, Place

import pygeoip
from settings import GEOIP_PATH
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

	request = kwargs.get('request', None)
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

	request = kwargs.get('request', None)
	obj = kwargs.get('object', None)
	ctype = kwargs.get('content_type', None)
	start = kwargs.get('start', 0)
	end = kwargs.get('end', 20)

	namespace['places'] = []

	#if theres a specific object set we want
	if obj is not None and obj != 'location':
		places = Place.objects.filter(object_pk=obj.pk)
		if len(places) == 1:
			namespace['places'] = places
	else:
		places = Place.objects.all()
		namespace['places'] = places

	#pass in a contenttype id, might be something else though
	if ctype is not None:
		#modified ctype string to hack in near_me requests, prepend 'ip_' to content type requests
		if ctype[0:2] == 'ip' and request is not None:
			if request == None:
				raise ValueError('Looks like request object is missing from a IP based lookup')
			ctype = ctype[2:]
			record = get_loc_by_ip(request)
			if record is not None:
				pt = {latitude: record['latitude'], longitude: record['longitude']}
				namespace['places'] = get_nearest(pt)
				namespace['near'] = True

		try:
			ctype = ContentType.objects.get(name=ctype)
		except:
			ctype = None
		namespace['places'] = namespace['places'].filter(content_type=ctype)

	if 'places' in namespace:
		if end-start == 1:
			namespace['places'] = namespace['places'][0]
		else:
			namespace['places'] = namespace['places'][start:end]

	output = nodelist.render(context)
	context.pop()

	return output


def get_loc_by_ip(request):
	ip = request.META.get('HTTP_X_REAL_IP', None)
	if ip is None:
		ip = request.META.get('REMOTE_ADDR', None)
		if ip is None:
			return False
	gi = pygeoip.GeoIP(GEOIP_PATH, pygeoip.STANDARD)
	return gi.record_by_addr(ip)


#location should be in format {'latitude' : 42, 'longtitude' : 3.14}
def get_nearest(self, here, ctype=None):
	if ctype is not None:
		return Place.objects.raw_query({'location' : {'$near' : here}, 'content_type': ctype})
	else:
		return Place.objects.raw_query({'location' : {'$near' : here}})
