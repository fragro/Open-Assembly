from oa_location.models import Place, Point
import simplejson
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType


def create_location(request):
    if not request.user.is_authenticated()  or not request.user.is_active or request.method != 'POST':
        #needs to popup registration dialog instead
        return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')

    if request.method == 'POST':
            object_pk = request.POST[u'object_pk']
            content_pk = request.POST[u'content_type']
            lat = request.POST[u'lat']
            lon = request.POST[u'lon']
            text = request.POST['desc']

            content_type = ContentType.objects.get(pk=content_pk)

            pt, is_new = Point.objects.get_or_create(latitude=lat, longtitude=lon)
            pt.save()

            if Place.objects.filter(object_pk=object_pk, content_type=content_type).count() > 0:
            	pl= Place.objects.get(object_pk=object_pk, content_type=content_type)
            	pl.text = text
            	pl.location = pt
            	pl.save()
            else:
            	loc = Place(summary=text, location=pt, object_pk=object_pk, content_type=content_type)
            	loc.save()

            return HttpResponse(simplejson.dumps({'FAIL': False, 'lat': lat, 'long': lon}),
                        mimetype='application/json')