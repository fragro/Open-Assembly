from oa_location.models import Place, Point, Location
import simplejson
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from pirate_permissions.models import has_permission
from django.template.loader import render_to_string


def access_location(obj, user):
    try:
        ifpop = (user == obj.user)
    except:
        ifpop = False
    if user == obj or ifpop or has_permission(obj, user):
        return True
    else:   
        return False

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

            obj = content_type.get_object_for_this_type(pk=object_pk)
            
            if access_location(obj, request.user):
                pt, is_new = Point.objects.get_or_create(latitude=lat, longtitude=lon)
                pt.save()
                loc, is_new = Location.objects.get_or_create(description = text)
                if Place.objects.filter(object_pk=object_pk, content_type=content_type).count() > 0:
                	pl= Place.objects.get(object_pk=object_pk, content_type=content_type)
                	pl.summary = loc
                	pl.location = pt
                	pl.save()
                else:
                	loc = Place(summary=loc, location=pt, object_pk=object_pk, content_type=content_type)
                	loc.save()

                return HttpResponse(simplejson.dumps({'FAIL': False, 'lat': lat, 'long': lon}),
                            mimetype='application/json')
            else:        
                return HttpResponse(simplejson.dumps({'FAIL': True, 'Permission': False}),
                                mimetype='application/json')


def delete_location(request):
    if not request.user.is_authenticated()  or not request.user.is_active or request.method != 'POST':
        #needs to popup registration dialog instead
        return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')

    if request.method == 'POST':
            object_pk = request.POST[u'object_pk']

            pl = Place.objects.get(object_pk=object_pk)
            if access_location(pl.content_object, request.user):
                pl.delete()
                return HttpResponse(simplejson.dumps({'FAIL': False}),
                    mimetype='application/json')
            else:
                return HttpResponse(simplejson.dumps({'FAIL': True, 'Permission': False}),
                    mimetype='application/json')


def load_markers(request):
    if not request.user.is_authenticated()  or not request.user.is_active:
        #needs to popup registration dialog instead
        return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')

    if request.method == 'GET':
            object_pk = request.GET[u'object_pk']
            content_pk = request.GET[u'content_type']
            start = request.GET[u'start']
            end = request.GET[u'end']
            dpk = request.GET[u'dashobj_pk']
            dim = request.GET[u'dimension']

            #generate context
            if object_pk != '':
                content_type = ContentType.objects.get(pk=content_pk)
                obj = content_type.get_object_for_this_type(pk=object_pk)
            else:
                obj = None
            
            context = {'request': request, 'object': obj, 'dashobj_pk': dpk, 'start': int(end), 'end': int(end)+1, 'dimension': dim }
            newmarkers = render_to_string('etc/markers.html', context)
            context = {'request': request, 'object': obj, 'dashobj_pk': dpk, 'start': int(end)+1, 'end': int(end)+2, 'dimension': dim }
            newlink = render_to_string('etc/load_markers.html', context)

            return HttpResponse(simplejson.dumps({'FAIL': False, 'html': newmarkers, 'link': newlink}),
                mimetype='application/json')