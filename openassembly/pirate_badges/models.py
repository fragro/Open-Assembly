from exceptions import ImportError, ValueError
from django.contrib import admin
from django.db import models
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_noop as _
from pirate_signals.models import notification_send

# Create your models here.

class BadgeType(models.Model):
    name = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.name
      
class BadgeDimension(models.Model):
    verbose_name = models.CharField(max_length=70, null=True, unique=True)
    name = models.CharField(max_length=70, null=True, unique=True)
    help_text = models.CharField(max_length=300, null=True, unique=True)
    badge_type = models.ForeignKey(BadgeType, null=True, unique=True)
    created_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now=True)
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_set_for_%(class)s",blank=True,null=True)
    test_int = models.IntegerField(blank=True,null=True) #argument for test function
    test_func = models.IntegerField(blank=True,null=True) #see below for test functions
        
    def __unicode__(self):
        return self.name

"""
Main badge model to tie badge dimensions to users
"""
class Badge(models.Model):
    user = models.ForeignKey(User)
    created_dt = models.DateTimeField(auto_now_add=True)
    dimension = models.ForeignKey(BadgeDimension)
    badge_type_id = models.IntegerField(_('Badge Type Id'), blank=True, null=True)
    
            
    def __unicode__(self):
        return self.user.username + ":" + self.dimension.name
    
    class Meta:
        unique_together = ("user", "dimension")
        
        
    def get_absolute_url(self):
        path = "/index.html#badges/_cbadge" + str(self.dimension.id)
        return path
        

def create_badge_dimension(verbose_name, name, help_text, badge_type, ctype, test_int, test_func):
    bt, is_new = BadgeType.objects.get_or_create(name=badge_type)
    bd, is_new = BadgeDimension.objects.get_or_create(verbose_name=verbose_name, 
                        name=name, help_text=help_text, 
                        badge_type=bt, content_type=ctype,
                        test_int=test_int, test_func=test_func)
    return bd
    
"""
Different methods for testing whether a user gets a badge or not,
tests may be count of contents created, actions taken and verified,
number of votes on that content, or tests unique to a single content type
"""

def check_badges(user, model, obj):
    new_badges = []
    ctype = ContentType.objects.get_for_model(model)
    dims = BadgeDimension.objects.filter(content_type=ctype)
    for bd in dims:
        try: b = Badge.objects.get(user=user,dimension=bd)
        except:
            savebadge = test_badge(obj, bd)
            if savebadge:
                b = Badge(user=user,dimension=bd, badge_type_id=bd.badge_type.id)
                b.save()
                notification_send.send(sender=b,obj=b,reply_to=b)

def test_badge(obj, bd, **kwargs):
    if bd.test_func == 1:
        return count_test({'model':bd.content_type.model_class(), 
                            'obj':obj, 'test_int':bd.test_int})
    elif bd.test_func == 2:
        return voted_on_test({'model':bd.content_type.model_class(),
                                    'test_int':bd.test_int, 'obj':obj})
    elif bd.test_func == 3:
        return count_test({'model':bd.content_type.model_class(), 
                            'obj':obj, 'test_int':bd.test_int})
    else: return False
    
def tag_test(args, **kwargs):
    model = args.get('model', None)
    obj = args.get('obj',None)
    x = args.get('test_int',None)
    ctype = ContentType.objects.get_for_model(Tag)
    objs = model.objects.filter(initiator=obj, ini_content_type=ctype)
    if objs.count() >= x: return True
    else: return False
    
def count_test(args, **kwargs):
    model = args.get('model', None)
    obj = args.get('obj',None)
    x = args.get('test_int',None)
    objs = model.objects.filter(user=obj)
    if objs.count() >= x: return True
    else: return False
    
    
def voted_on_test(args, **kwargs):
    model = args.get('model', None)
    x = args.get('test_int',None)
    obj = kwargs.get('obj', None)
    objs = model.objects.filter(object_pk=obj) 
    if objs.count() >= x: return True
    else: return False
    
    
admin.site.register(Badge)
admin.site.register(BadgeDimension)
admin.site.register(BadgeType)
