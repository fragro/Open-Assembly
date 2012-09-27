from django.db import models
from django.contrib import admin

# Create your models here.
class Register(models.Model):
    name = models.CharField(max_length=140, unique = True)
    password1 = models.CharField(max_length=600)
    password2 = models.CharField(max_length=600)
    email = models.CharField(max_length=600, unique=True)

# Create your models here.
class Login(models.Model):
    name = models.CharField(max_length=140)
    password = models.CharField(max_length=600, null=True, blank=True)
    ip = models.IPAddressField()
    created_dt = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    
    
    def __str__(self):
        return u'[%s:%s]' % (self.name, self.created_dt)

