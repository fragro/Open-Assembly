from multiprocessing import Pool
from StringIO import StringIO

import boto
from django.conf import settings

from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType

from ajaxuploader.backends.base import AbstractUploadBackend
from django.core.files.uploadedfile import InMemoryUploadedFile
import mimetypes

from pirate_sources.models import IMGSource

import PIL


class S3CustomBackend(AbstractUploadBackend):

	def upload_chunk(self, chunk):
		self.buffer.write(chunk)
		

	def setup(self, filename):
		self.buffer = StringIO()

	def upload_complete(self, request, filename):
		# Tie up loose ends, and finish the upload
		#create an imgsource
		
		try:
			print '*' * 80
			print request.session.items()
			object_pk = request.session.get('object_pk')
			#if there is not currently a current image we create one. if it exists, remove it's current value and create new
			img, is_new = IMGSource.objects.get_or_create(object_pk=object_pk, current=True)
			if not is_new:
				img.current = False
				img.save()
				img = IMGSource(object_pk=object_pk, current=True)
			#user
			userpk = request.session.get('_auth_user_id')
			img.user = User.objects.get(pk=userpk)
			print
			#contenttype
			ctype = request.session.get('content_pk')
			print ctype
			img.content_type = ContentType.objects.get(pk=ctype)
			#objectid
			self.buffer.seek(0)
			mimetypes.init()
			mime = mimetypes.guess_type(filename)
			image = InMemoryUploadedFile(self.buffer, filename, filename, mime[0], self.buffer.len, None)
			img.file = image
			img.save()

			print img.file.url
			img.file.url = "http://www.google.com"
			img.save()
			self.buffer.close()

		except Exception, e:
			return {'pk': str(e)}
	

		return {'pk': img.pk}
