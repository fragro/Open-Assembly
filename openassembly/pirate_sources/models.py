from django.db import models
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

import PIL
from PIL import Image
from StringIO import StringIO

from django.core.files.uploadedfile import InMemoryUploadedFile


###TODO: Need to make Sources generic so we can use them for issues/solutions/arguments as well
class URLSource(models.Model):
    url = models.URLField(max_length=200, null=True, blank=True)
    submit_date = models.DateTimeField(_('date/time submitted'), auto_now_add=True)
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_set_for_%(class)s")
    object_pk = models.CharField(_('object ID'), max_length=100)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    user = models.ForeignKey(User)
    is_video = models.BooleanField()

    def __unicode__(self):
        return self.url


class IMGSource(models.Model):
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_set_for_%(class)s", blank=True, null=True)
    object_pk = models.CharField(_('object ID'), max_length=100, blank=True, null=True)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    user = models.ForeignKey(User, null=True, blank=True)
    file = models.ImageField(upload_to='static/%Y/%m/%d/%H/%M/%S/')

    submit_date = models.DateTimeField(_('date/time submitted'), auto_now_add=True)
    url = models.CharField(max_length=200)
    current = models.BooleanField()
    private = models.BooleanField(default=False)

    def make(self, image, thumb_field_name):
        im = PIL.Image.open(StringIO(''.join(image.chunks())))
        im_io = StringIO()
        im.save(im_io, im.format)

        image = InMemoryUploadedFile(im_io, thumb_field_name, '%s.jpg' % image.name.rsplit('.', 1)[0], 'image/jpeg', im_io.len, None)
        im = PIL.Image.open(StringIO(''.join(image.chunks())))

        src_width, src_height = im.size

        if src_width > src_height:
            small = (46, 40)
            medium = (70, 90)
            large = (190, 220)
        else:
            small = (40, 36)
            medium = (90, 70)
            large = (220, 190)
        im_io = StringIO()
        im.thumbnail(small, Image.ANTIALIAS)
        im.save(im_io, im.format)
        """
        thumbnail_small = InMemoryUploadedFile(im_io, thumb_field_name, '%s_thumbsmall.jpg' % image.name.rsplit('.', 1)[0], 'image/jpeg', im_io.len, None)
        im = PIL.Image.open(StringIO(''.join(image.chunks())))

        im_io = StringIO()
        im.thumbnail(medium, Image.ANTIALIAS)
        im.save(im_io, im.format)

        thumbnail = InMemoryUploadedFile(im_io, thumb_field_name, '%s_thumb.jpg' % image.name.rsplit('.', 1)[0], 'image/jpeg', im_io.len, None)
        im = PIL.Image.open(StringIO(''.join(image.chunks())))

        im_io = StringIO()
        im.thumbnail(large, Image.ANTIALIAS)

        im.save(im_io, im.format)

        thumbnail_large = InMemoryUploadedFile(im_io, thumb_field_name, '%s_thumblarge.jpg' % image.name.rsplit('.', 1)[0], 'image/jpeg', im_io.len, None)
        """
        self.file = image
        self.save()

    def rescale(self, data, width, height, force=True):
        """Rescale the given image, optionally cropping it to make sure the result image has the specified width and height."""

        image = Image.open(data.path)

      # normalize image mode
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.thumbnail((width, height), Image.ANTIALIAS)
        image.save(data.path, 'JPEG', quality=100)
        """
        img = data
        if not force:
            img.thumbnail((max_width, max_height), PIL.Image.ANTIALIAS)
        else:
            src_width, src_height = img.size
            src_ratio = float(src_width) / float(src_height)
            dst_width, dst_height = max_width, max_height
            dst_ratio = float(dst_width) / float(dst_height)

            if dst_ratio < src_ratio:
                crop_height = src_height
                crop_width = crop_height * dst_ratio
                x_offset = float(src_width - crop_width) / 2
                y_offset = 0
            else:
                crop_width = src_width
                crop_height = crop_width / dst_ratio
                x_offset = 0
                y_offset = float(src_height - crop_height) / 3
            img = img.crop((x_offset, y_offset, x_offset + int(crop_width), y_offset + int(crop_height)))
            img = img.resize((dst_width, dst_height), PIL.Image.ANTIALIAS)
"""
        return img

    @property
    def filename(self):
        return self.file.name.rsplit('/', 1)[-1]

    def __unicode__(self):
        return str(self.user) + " object_pk: " + str(self.object_pk) + " " + str(self.current)

"""
Video source files stored and accessed via amazon S3 for OpenAssembly 
"""
class VideoSource(models.Model):
    submit_date = models.DateTimeField(_('date/time submitted'), auto_now_add=True)
    bars = models.IntegerField() # 
    video_id = models.IntegerField(null=True,blank=True)
    filename = models.CharField(max_length=50,null=True,blank=True)
    
        
    def __unicode__(self):
        return str(self.id)
    

admin.site.register(VideoSource)
admin.site.register(URLSource)
admin.site.register(IMGSource)
