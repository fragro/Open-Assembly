from django.template import Context, loader
from pirate_issues.models import Issue, Topic#, Argument
from django.http import HttpResponse
from django.views.generic.list_detail import object_list
from annoying.decorators import render_to, ajax_request
from annoying.helpers import get_object_or_404_ajax
from django.shortcuts import get_object_or_404,render_to_response
import datetime

#Queryset is list of all Topics
def get_all_topics(request, *args, **kwargs):
	kwargs['queryset'] = Topic.objects.all()
	return object_list(request, *args, **kwargs)
	
#Returns queryset of Issues with Topic.pk = topic_id
def get_topic(request, topic_id, *args, **kwargs):
	topic = get_object_or_404(Topic, id=topic_id)
	kwargs['queryset'] = Issue.objects.filter(topic__id__exact=topic_id)
	if not kwargs.has_key('extra_context'):
		kwargs['extra_context'] = {}
	kwargs['extra_context']['topic'] = topic
 	return object_list(request, *args, **kwargs)

#Returns a single issue, with associated Argument objects as the queryset
def	get_issue(request, issue_id, *args, **kwargs):
	issue = get_object_or_404(Issue, id=issue_id)
	kwargs['queryset'] = Argument.objects.filter(issue__id__exact=issue_id)
	if not kwargs.has_key('extra_context'):
		kwargs['extra_context'] = {}
	kwargs['extra_context']['issue'] = issue
 	return object_list(request, *args, **kwargs)

#Returns argument by ID, need to return comments as well but that is dependent on oa-deliberation module
def get_argument_w_id(request, arg_id, *args, **kwargs):
	argument = get_object_or_404(Argument, id=arg_id)
	if not kwargs.has_key('extra_context'):
		kwargs['extra_context'] = {}
	kwargs['extra_context']['argument'] = argument
 	return object_list(request, *args, **kwargs)
