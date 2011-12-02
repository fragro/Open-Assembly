from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from django.contrib.contenttypes.models import ContentType
import datetime
from django.contrib.auth.models import User

from django.core.files.base import ContentFile

from pirate_sources.templatetags.sourcetags import IMGSourceForm
from pirate_sources.models import IMGSource

from filetransfers.api import prepare_upload, serve_file


def change_avatar(request, obj_pk=None, new_pk=None, ctype_pk=None):
    view_url = reverse('pirate_sources.views.upload_handler', args=[obj_pk, ctype_pk])
    try:
        oldimg = IMGSource.objects.get(object_pk=obj_pk, current=True)
        oldimg.current = False
        oldimg.save()
    except:
        pass
    if obj_pk != new_pk:
        newimg = IMGSource.objects.get(pk=new_pk)
        newimg.current = True
        newimg.save()
        return HttpResponseRedirect(view_url)


def upload_handler(request, obj_pk=None, ctype_pk=None):
    view_url = reverse('pirate_sources.views.upload_handler', args=[obj_pk, ctype_pk])
    if request.method == 'POST':
        form = IMGSourceForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                img = form.save()
                img.user = request.user
                img.object_pk = obj_pk
                img.content_type = ContentType.objects.get(pk=ctype_pk)
                img.submit_date = datetime.datetime.now()

                #file_content = ContentFile(request.FILES['file'].read())
                #img.file.save(str(img.object_pk) + '_' + str(img.content_type), file_content)
                img.make(request.FILES['file'], img.file.name)
                #photo_key = str(img.file.file.blobstore_info.key())
                url = img.file.path
                if img.private != True:
                    try:
                        oldimg = IMGSource.objects.get(object_pk=obj_pk, current=True)
                        oldimg.current = False
                        oldimg.save()
                    except:
                        pass
                    img.current = True
                img.url = url
                img.save()
            else:
                view_url += '?error=Not a valid image'
            return HttpResponseRedirect(view_url)
        except Exception, e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error('caught %s in image upload', e)
            #raise e

    upload_url, upload_data = prepare_upload(request, view_url)
    form = IMGSourceForm()

    uploads = IMGSource.objects.filter(object_pk=obj_pk)

    ctypemod = ContentType.objects.get(pk=ctype_pk)
    m = ctypemod.model_class()
    obj = m.objects.get(pk=obj_pk)
    return direct_to_template(request, 'upload.html',
        {'form': form, 'upload_url': upload_url, 'upload_data': upload_data, 'object': obj,
         'uploads': uploads, 'obj_pk': obj_pk, 'ctype_pk': ctype_pk, 'error': request.GET.get('error')})

def download_handler(request, pk):
    upload = get_object_or_404(IMGSource, pk=pk)
    return serve_file(request, upload.file, save_as=True)

def delete_handler(request, pk, ctype_pk):
    get_object_or_404(IMGSource, pk=pk).delete()
    return HttpResponseRedirect(reverse('pirate_sources.views.upload_handler'), args=[pk, ctype_pk])
