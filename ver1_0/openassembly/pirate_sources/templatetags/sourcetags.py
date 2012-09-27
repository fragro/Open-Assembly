from django import template
from django import forms
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from pirate_sources.models import IMGSource, URLSource
from pirate_core.views import HttpRedirectException, namespace_get
from django.template import Library
from django.core.urlresolvers import reverse
import re
from django.core.cache import cache
from py_etherpad import EtherpadLiteClient
import datetime

from settings import ETHERPAD_API
from filetransfers.api import prepare_upload

from django.conf import settings

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_source')


@block
def pp_set_livestreamcache(context, nodelist, *args, **kwargs):
	"""
	Retrieves the current image for this object id.
	"""
	context.push()
	namespace = get_namespace(context)

	user = kwargs.get('user', None)
	obj = kwargs.get('object', None)

	cache.set(str(user.pk) + '-livestream', obj.pk)
	output = nodelist.render(context)
	context.pop()

	return output


@block
def pp_check_livestreamcache(context, nodelist, *args, **kwargs):
	"""
	Retrieves the current image for this object id.
	"""
	context.push()
	namespace = get_namespace(context)

	user = kwargs.get('user', None)

	namespace['livestream'] = cache.get(str(user.pk) + '-livestream')
	output = nodelist.render(context)
	context.pop()

	return output


@block
def pp_get_pad(context, nodelist, *args, **kwargs):
	"""
	Retrieves the current image for this object id.
	"""
	context.push()
	namespace = get_namespace(context)

	obj = kwargs.get('object', None)

	myPad = EtherpadLiteClient(ETHERPAD_API, 'http://notes.occupy.net/api')
	try:
		if ETHERPAD_API != None:
			#Change the text of the etherpad
			try:
				text = myPad.getHtml(str(obj.pk))
			except:
				myPad.createPad(str(obj.pk), '')
				text = myPad.getHtml(str(obj.pk))

			namespace['text'] = text['html']
		else:
			namespace['text'] = '<p>No API Key</p>'
	except:
		namespace['text'] = '<p>Looks like the Occupy.net Etherpad server is down... Thanks for your patience</p>'

	output = nodelist.render(context)
	context.pop()

	return output


@block
def pp_current_image(context, nodelist, *args, **kwargs):
	"""
	Retrieves the current image for this object id.
	"""
	context.push()
	namespace = get_namespace(context)

	obj = kwargs.get('object', None)

	if obj is not None:
		try:
			imgsource = IMGSource.objects.get(object_pk=obj.pk, current=True)
			namespace['current_img'] = imgsource
		except:
			imgsource = IMGSource.objects.filter(object_pk=obj.pk)
			if len(imgsource) > 0:
				namespace['current_img'] = imgsource

	output = nodelist.render(context)
	context.pop()

	return output


@block
def pp_get_contenttype_id(context, nodelist, *args, **kwargs):
	
	context.push()
	namespace = get_namespace(context)

	obj = kwargs.get('object',None)
	
	if obj is not None and not isinstance(obj, basestring): 
		pk = ContentType.objects.get_for_model(obj).pk
		namespace['ctype_pk'] = pk
	
	output = nodelist.render(context)
	context.pop()

	return output
	

@block
def pp_get_iframe_video(context, nodelist, *args, **kwargs):
	"""
	This function grabs an VideoSource object and populates and 
	video_iframe.html file for that video, if one has not yet been
	created. There is no way for the iframe src argument to 
	evaluate django template code, so this is the solution that
	presents itself.
	
	"""
	
	context.push()
	namespace = get_namespace(context)

	obj = kwargs.get('object',None)
	
	if obj != None:
		pass
	   # htmllink = generate_iframe(obj.video)
		#namespace['link'] = htmllink
	else: raise ValueError("Submitted 'object' as NoneType to pp_get_iframe_video")
			
	output = nodelist.render(context)
	context.pop()

	return output

def generate_iframe(vid):
	html = """
	<html>
<head>
  <title>Poptastic</title>
  <link href="/static/html5_video_voting/stylesheets/app.css" media="screen" rel="stylesheet" type="text/css">
  <script src="/static/html5_video_voting/javascripts/jquery.js" type="text/javascript"></script>
<script src="/static/html5_video_voting/javascripts/jquery-ui.js" type="text/javascript"></script>
<script src="/static/html5_video_voting/javascripts/raphaeljs/raphael.js" type="text/javascript"></script>
<script src="/static/html5_video_voting/javascripts/raphaeljs/g.raphael.js" type="text/javascript"></script>
<script src="/static/html5_video_voting/javascripts/raphaeljs/bar.raphael.js" type="text/javascript"></script>
<script src="/static/html5_video_voting/javascripts/application.js" type="text/javascript"></script>
<style>body {margin: 0;padding: 0;overflow: hidden;}</style></head><body><div id="poptastic">
	<video id=" 
""" + str(vid.id) + '"class="video" data-ip="f528764d624db129b32c21fbca0cb8d6" data-keycode="32" data-bars="' + str(vid.bars) + '" width="600" height="340"><source src="' + str(vid.filename_mp4) + """ " type='video/mp4; codecs="avc1.42E01E, mp4a.40.2"'>
			<source src=" """ + str(vid.filename_webm) + """ " type='video/webm; codecs="vp8, vorbis"'>			
			<source src=" """ + str(vid.filename_ogg) + """" type='video/ogg; codecs="theora, vorbis"'>
			
		</video>
	<div id="controls">
		<a href="#pause" id="play">Play</a>
		<div id="bar-wrapper-container">
		<div id="bar-wrapper">
			<div id="bar"></div>
			<div id="buffer"></div>
			<a href="#" id="paddle" class="ui-draggable"></a>
		</div>
		</div>
		<a href="#vol" id="volume"><span></span></a>
	</div>
	<div id="chart"></div>
</div>
<div id="error">You must be logged in to vote!</div>
</body>
</html>"""
	return html


@block
def pp_get_source(context, nodelist, *args, **kwargs):
	context.push()
	namespace = get_namespace(context)

	obj = kwargs.get('object', None)
	t = kwargs.get('type', None)

	src = None
	try:
		if obj is not None:
			if t == 'url':
				src = URLSource.objects.get(pk=obj.pk)
			elif t == 'img':
				src = IMGSource.objects.get(pk=obj.pk)
	except:
		pass

	namespace['src'] = src

	output = nodelist.render(context)
	context.pop()

	return output


@block
def pp_calculate_size(context, nodelist, *args, **kwargs):
	context.push()
	namespace = get_namespace(context)

	w = kwargs.get('width', None)
	h = kwargs.get('height', None)
	img = kwargs.get('img', None)

	if img is not None:
		img_w = img.file.width
		img_h = img.file.height

		if w is not None and h is not None:
			if int(img_w) > 581:
				namespace['width'] = '100%'
			else:
				namespace['width'] = int(min(int(img_w), int(w)/1.625))
			namespace['geometry'] = str(int(min(int(img_w), int(w)/1.625)))
		else:
			if int(img_w) > 581:
				namespace['width'] = '100%'
			else:
				namespace['width'] = str(img_w) + 'px'
			namespace['geometry'] = str(img_w)

	output = nodelist.render(context)
	context.pop()

	return output

@block
def pp_get_sources(context, nodelist, *args, **kwargs):
	context.push()
	namespace = get_namespace(context)

	obj = kwargs.get('object', None)
	t = kwargs.get('type', None)
	get = kwargs.get('get', None)


	try:
		if obj is not None:
			content_type = ContentType.objects.get_for_model(obj)
			namespace['ctype'] = content_type.pk
			if t == 'url':
				namespace['sources'] = URLSource.objects.filter(object_pk=obj.pk, is_video=False)
			#namespace['videosource_list'] = URLSource.objects.filter(object_pk=obj.pk, is_video=True)
			elif t == 'img':
				if get == "all":
					l = IMGSource.objects.filter(object_pk=obj.pk).order_by('submit_date')
					namespace['sources'] = l
					cnt = l.count()
					namespace['count'] = cnt
				else:
					try:
						namespace['cur_img'] = IMGSource.objects.get(object_pk=obj.pk, current=True)
					except:
						namespace['cur_img'] = None
						try:
							namespace['cur_img'] = IMGSource.objects.get(pk=obj.pk, current=True)
						except:
							pass

	except:
		namespace['cur_img'] = None
		namespace['sources'] = []

	output = nodelist.render(context)
	context.pop()

	return output



@block
def pp_ajaximg(context, nodelist, *args, **kwargs):
	"""
	Modifies the request session data to prep it for AJAX requests to the Ajax image uploader.
	"""
	context.push()
	namespace = get_namespace(context)
	request = kwargs.get('request', None)
	obj = kwargs.get('object', None)

	if obj is not None and request is not None:
		ctype = ContentType.objects.get_for_model(obj)

		request.session['object_pk'] = obj.pk
		request.session['content_pk'] = ctype.pk

	output = nodelist.render(context)
	context.pop()

	return output


@block
def pp_imgsource_form(context, nodelist, *args, **kwargs):
	'''
	This block tag can create or process forms eitfrom genericview.views import HttpRedirectException, namespace_gether to create or to modify arguments.
	Usage is as follows:

	{% pp_topic_form POST=request.POST path=request.path topic=pp_topic.topic root=some_topic %}
	   Do stuff with {{ pp_source.form }}.
	{% endpp_topic_form %}
	'''
	context.push()
	namespace = get_namespace(context)

	POST = kwargs.get('POST', None)
	FILE = kwargs.get('FILE', None)
	obj = kwargs.get('object', None)
	request = kwargs.get('request', None)

	content_type = ContentType.objects.get_for_model(obj)

	view_url = reverse('pirate_sources.views.upload_handler', args=[obj.pk, content_type.pk])
	if POST:
		form = IMGSourceForm(POST, FILE)
		if form.is_valid():
			img = form.save()
			img.user = request.user
			img.object_pk = obj.pk
			img.content_type = ContentType.objects.get(pk=content_type.pk)
			img.submit_date = datetime.datetime.now()

			img.make(request.FILES['file'], img.file.name)
			if img.private != True:
				try:
					oldimg = IMGSource.objects.get(object_pk=obj.pk, current=True)
					oldimg.current = False
					oldimg.save()
				except:
					pass
				img.current = True
			img.save()
			upload_url, upload_data = prepare_upload(request, view_url)
			form = IMGSourceForm()
		else:
			view_url += '?error=Not a valid image'
		namespace['errors'] = form.errors

	upload_url, upload_data = prepare_upload(request, view_url)
	form = IMGSourceForm()

	namespace['upload_url'] = upload_url
	namespace['upload_data'] = upload_data
	namespace['form'] = form
	output = nodelist.render(context)
	context.pop()

	return output


class IMGSourceForm(forms.ModelForm):

	def save(self, commit=True):
		new_source = super(IMGSourceForm, self).save(commit=commit)
		return new_source

	class Meta:
		model = IMGSource
		exclude = ('user', 'title', 'url', 'current', 'thumbnail', 'thumbnail_small', 'thumbnail_large', 'content_type', 'object_pk')

	form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_imgsource_form")


@block
def pp_videosource_form(context, nodelist, *args, **kwargs):
	'''
	This block tag can create or process forms eitfrom genericview.views import HttpRedirectException, namespace_gether to create or to modify arguments.
	Usage is as follows:

	{% pp_topic_form POST=request.POST path=request.path topic=pp_topic.topic root=some_topic %}
	   Do stuff with {{ pp_source.form }}.
	{% endpp_topic_form %}
	'''
	context.push()
	namespace = get_namespace(context)

	POST = kwargs.get('POST', None)
	source = kwargs.get('source', None)
	obj = kwargs.get('object', None)
	user = kwargs.get('user', None)

	if POST and POST.get("form_id") == "pp_videosource_form":
		form = VideoSourceForm(POST) if source is None else VideoSourceForm(POST, instance=source)
		if form.is_valid():
			new_source = form.save(commit=False)
			new_source.user = user
			new_source.content_type = ContentType.objects.get_for_model(obj.__class__)
			new_source.object_pk = obj.pk
			new_source.content_object = obj
			url = parse_video_url(form.cleaned_data['url'])
			if url != None:
				new_source.url = url
				new_source.is_video = True
				try:
					source = URLSource.objects.get(url=url, object_pk=obj.pk)
				except:
					new_source.save()
				#raise HttpRedirectException(HttpResponseRedirect(obj.get_absolute_url()))
			else:
				namespace['errors'] = "Not a valid youtube URL"
		else:
			namespace['errors'] = "Not a valid URL"
		#path = obj.get_absolute_url()
		#raise HttpRedirectException(HttpResponseRedirect(path))
	else:
		form = VideoSourceForm() if source is None else VideoSourceForm(instance=source)

	namespace['urlform'] = form
	output = nodelist.render(context)
	context.pop()

	return output


def parse_video_url(url):
	#TODO: Need to update this, it only accepts a limited number of youtube urls

	l = re.split('\/', url)
	try:
		if l[-1][0:8] == 'watch?v=':
			return l[-1][8:]
	except:
		if l[-1] != '':
			return l[-1]
	else:
		return None


@block
def pp_urlsource_form(context, nodelist, *args, **kwargs):
	'''
	This block tag can create or process forms eitfrom genericview.views import HttpRedirectException, namespace_gether to create or to modify arguments.
	Usage is as follows:

	{% pp_topic_form POST=request.POST path=request.path topic=pp_topic.topic root=some_topic %}
	   Do stuff with {{ pp_source.form }}.
	{% endpp_topic_form %}
	'''
	context.push()
	namespace = get_namespace(context)

	POST = kwargs.get('POST', None)
	source = kwargs.get('source', None)
	obj = kwargs.get('object', None)
	user = kwargs.get('user', None)

   # print request
   # print "WTF?"

	if POST and POST.get("form_id") == "pp_urlsource_form":
		form = URLSourceForm(POST) if source is None else URLSourceForm(POST, instance=source)
		if form.is_valid():
			new_source = form.save(commit=False)
			new_source.user = user
			new_source.content_type = ContentType.objects.get_for_model(obj.__class__)
			new_source.object_pk = obj.pk
			new_source.content_object = obj
			new_source.is_video = False
			new_source.save()
			form = URLSourceForm()
		else:
			namespace['errors'] = "Not a valid URL"
		#raise HttpRedirectException(HttpResponseRedirect(path))
	else:
		form = URLSourceForm() if source is None else URLSourceForm(instance=source)

	namespace['urlform'] = form
	output = nodelist.render(context)
	context.pop()

	return output


class URLSourceForm(forms.ModelForm):

	def save(self, commit=True):
		new_source = super(URLSourceForm, self).save(commit=commit)
		return new_source

	class Meta:
		model = URLSource
		exclude = ('content_type', 'object_pk', 'content_object', 'user')

	form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_urlsource_form")
	url = forms.CharField(initial="http://")


class VideoSourceForm(forms.ModelForm):

	def save(self, commit=True):
		new_source = super(VideoSourceForm, self).save(commit=commit)
		return new_source

	class Meta:
		model = URLSource
		exclude = ('content_type', 'object_pk', 'content_object', 'user')

	form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_videosource_form")
