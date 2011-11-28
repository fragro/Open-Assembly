from django.conf.urls.defaults import *
from handlers import ContentHandler, UserHandler, GroupContentHandler, VoteHandler, PKHandler, PlatformHandler, PlatformDimensionHandler
from piston.resource import Resource

content_handler = Resource(ContentHandler)
user_handler = Resource(UserHandler)
vote_handler = Resource(VoteHandler)
pk_handler = Resource(PKHandler)
platform_handler = Resource(PlatformHandler)
groupcontent_handler = Resource(GroupContentHandler)
platformdim_handler = Resource(PlatformDimensionHandler)


urlpatterns = patterns('',
   url(r'^content/(?P<app>[^/]+)/(?P<model>[^/]+)/(?P<obj_id>[^/]+)/', content_handler),
   url(r'^content/(?P<app>[^/]+)/(?P<model>[^/]+)/', content_handler),
   url(r'^content/', content_handler),
   url(r'^groupcontent/(?P<parent>[^/]+)/', groupcontent_handler),
   url(r'^user/(?P<obj_id>[^/]+)/', user_handler),
   url(r'^user/', user_handler),
   url(r'^vote/(?P<model>[^/]+)/(?P<obj_id>[^/]+)/', vote_handler),
   url(r'^vote/(?P<obj_id>[^/]+)/', vote_handler),
   url(r'^vote/', vote_handler),
   url(r'^pks/(?P<pk_type>[^/]+)/', pk_handler),
   url(r'^platforms/(?P<app>[^/]+)/(?P<model>[^/]+)/(?P<obj_id>[^/]+)/', platform_handler),
   url(r'^platforms/(?P<obj_id>[^/]+)/', platformdim_handler),
   url(r'^platforms/', platformdim_handler),\
)