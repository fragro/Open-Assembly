from django.db import models
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django import forms 


###TODO: Need to make Sources generic so we can use them for issues/solutions/arguments as well
class URLSource(models.Model):
    url = models.URLField(max_length=200, null=True, blank=True)
    submit_date = models.DateTimeField(_('date/time submitted'), auto_now_add=True)
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_set_for_%(class)s")
    object_pk = models.IntegerField(_('object ID'))
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    user = models.ForeignKey(User)
    is_video = models.BooleanField()

    def __unicode__(self):
        return self.url


class IMGSource(models.Model):
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_set_for_%(class)s",blank=True,null=True)
    object_pk = models.IntegerField(_('object ID'),blank=True,null=True)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")   
    user = models.ForeignKey(User, null=True, blank=True)
    file = models.ImageField(upload_to='uploads/%Y/%m/%d/%H/%M/%S/')
    submit_date = models.DateTimeField(_('date/time submitted'), auto_now_add=True)
    url = models.CharField(max_length=200)
    current = models.BooleanField()
    private = models.BooleanField(default=False)

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
