from django.db import models

# Create your models here.
from piston.handler import BaseHandler
from myapp.models import Blogpost

class BlogpostHandler(BaseHandler):
   allowed_methods = ('GET',)
   model = Blogpost   

   def read(self, request, post_slug):