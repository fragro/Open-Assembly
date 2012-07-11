from django.conf.urls.defaults import *
from pirate_issues import views

urlpatterns = patterns('',
    url(r'topics/', views.get_all_topics, name="topic_list"),
    url(r'topic/(?P<topic>\d+)/$', views.get_topic, name="get_topic"),
  #  url(r'upvote/(?P<topic>\d+)/(?P<issue_id>\d+)/$', views.upvote, name="upvote"),
  #  url(r'downvote/(?P<topic>\d+)/(?P<issue_id>\d+)/$', views.downvote, name="downvote"),
  #  url(r'neutvote/(?P<topic>\d+)/(?P<issue_id>\d+)/$', views.neutvote, name="neutvote"),


)
