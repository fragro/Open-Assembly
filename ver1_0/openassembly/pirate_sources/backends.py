from multiprocessing import Pool
from StringIO import StringIO

import boto
from django.conf import settings

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
			img = IMGSource()
			self.buffer.seek(0)
			mimetypes.init()
			mime = mimetypes.guess_type(filename)
			image = InMemoryUploadedFile(self.buffer, filename, filename, mime[0], self.buffer.len, None)
			img.file = image
			img.save()
			self.buffer.close()

		except Exception, e:
			return {'pk': str(e)}
	

		return {'pk': img.pk}
