import dselector
import settings

from django.views.generic.simple import direct_to_template
from django.views.generic.create_update import delete_object
from django.views.decorators.csrf import csrf_protect
from django.conf.urls.defaults import *
from django.contrib import admin
from pirate_core import redirectable, home_page, welcome_page
from ajaxapi.views import vote, generate_vote_content, delete_source, add_tag, starvote, spectrumvote, add_group, remove_group
from ajaxapi.views import flagvote, set_loc_by_ip, del_tag, add_video_vote, update_video_votes, remove_platform
from ajaxapi.views import setup_admin, confirm, add_platform, change_hash_dim, change_hash_ctype, delete_object
from pirate_login.views import logout_view

from oa_cache.views import load_page, nuke_memcache, update_ranks, side_effect
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm

#autodiscovery

import search
try:
    search.autodiscover()
except:
    pass

import object_tools

object_tools.autodiscover()

urlpatterns = patterns('',
    (r'^object-tools/', include(object_tools.tools.urls)),
)

from dbindexer import autodiscover
autodiscover()

admin.autodiscover()

#patterns

parser = dselector.Parser()
parser.register("file", r'[\w0-9\_]+\.?[\w0-9\_]*')

urlpatterns = patterns('',
    (r'^$', welcome_page),
    (r'^tulsa/', home_page),
    (r'^politics/', welcome_page),
    (r'^politics', welcome_page),
    (r'^add_video_vote/', add_video_vote),
    (r'^update_video_votes/', update_video_votes),
    #(r'^copy_comment/',  pirate_comment_fix),
    (r'^admin/', include(admin.site.urls)),
    (r'^setup_admin/', setup_admin),
    (r'^sourcedelete/(?P<object_id>\d+)/(?P<consensus_id>\d+)/$', delete_source),
    (r'^objectdelete/', delete_object),
    (r'^vote/', vote),
    (r'^starvote/', starvote),
    (r'^flagvote/', flagvote),
    (r'^set_loc_by_ip/', set_loc_by_ip),
    (r'^spectrumvote/', spectrumvote),
    (r'^add_tag/', add_tag),  #ajax
    (r'^add_group/', add_group),  #ajax
    (r'^remove_group/', remove_group),  #ajax
    (r'^del_tag/', del_tag),  #ajax
    (r'^change_hash_dim/', change_hash_dim),  #ajax
    (r'^change_hash_ctype/', change_hash_ctype),  #ajax
    (r'^add_platform/', add_platform),
    (r'^remove_platform/', remove_platform),
    (r'^generate_vote_content/', generate_vote_content),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^markitup/', include('markitup.urls')),
    (r'^logout/', logout_view),
    (r'^load_page/', load_page),
    (r'^side_effect/', side_effect),
    (r'^confirm/(?P<key>[0-9A-Za-z_\-]+)/$', confirm),
    (r'^tasks/update_ranks/', update_ranks),
    (r'^tasks/nuke_memcache/', nuke_memcache),

)

urlpatterns += patterns('',
    (r'^password_reset/$', 'django.contrib.auth.views.password_reset', {'template_name':'password_reset.html'}),
    (r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done', {'template_name':'password_reset_complete.html'}),
    (r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name':'password_reset_confirm.html'}),
    (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete', {'template_name':'password_reset_done.html'}),
)

urlpatterns += parser.patterns('',
    (r'{template:file}', csrf_protect(redirectable(direct_to_template)), {}, "pp-page"),
)

urlpatterns += patterns('pirate_sources.views',
    (r'^upload/(?P<obj_pk>[0-9A-Za-z_\-]+)/(?P<ctype_pk>[0-9A-Za-z_\-]+)/$', 'upload_handler'),
    (r'^upload/$', 'upload_handler'),
    (r'^download/(?P<pk>[0-9A-Za-z_\-]+)$', 'download_handler'),
    (r'^delete/(?P<pk>[0-9A-Za-z_\-]+)/(?P<ctype_pk>[0-9A-Za-z_\-]+)/$', 'delete_handler'),
    (r'^change/(?P<obj_pk>[0-9A-Za-z_\-]+)/(?P<new_pk>[0-9A-Za-z_\-]+)/(?P<ctype_pk>[0-9A-Za-z_\-]+)/$', 'change_avatar'),
)
urlpatterns += patterns('ajaxapi.views',
    (r'^add_support/(?P<pk>.+)$', 'add_support'),
    (r'^remove_support/(?P<pk>.+)$', 'remove_support'),
    (r'^live_search/$', 'live_search'),
)

urlpatterns += patterns('',
   # all my other url mappings
   (r'^api/', include('api.urls')),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
   )
