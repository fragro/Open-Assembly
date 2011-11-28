# -*- coding: latin-1 -*-
"""
========
Fake-PIL
========
By: `UYSRC <http://www.uysrc.com/>`_
Date: Fri, Jan 14, 2011

PIL interface overtop Google Imaging API to enable
Django-nonrel model.ImageField work with 
django-filetransfers.  Validates whether the file 
uploaded is indeed an image.  

Released into the public domain, creative commons, 
take it, break it, and make it better license

Copyright ©®@℗ 
No warranties, no guarantees

Usage
=====
1. Put the contents of this file in a substitute "PIL" 
module in your django-nonrel project folder, ALA::

    {PROJECT_FOLDER}/PIL/__init__.py 
    
2. Then go ahead and make a simple "app" w/ a model which 
contains a django ImageField

3. Test the "app" in an admin form, or via your own form class
  --> Make sure to test both upload and edit functionality!

4. No more ImportError: No module named PIL

Danke schön
===========
Thank you to Waldemar Kornewald and davepeck

http://groups.google.com/group/django-non-relational/msg/47765a6f078f073b
http://djangosnippets.org/snippets/1805/

"""
import logging
from google.appengine.api import images

class Image(object):
    __instances = {}

    """
    Wrapper class around Google Imaging API to provide sufficient
    support for Django's ImageField in django-nonrel running on 
    Google AppEngine.  This is not meant as a replacement for PIL!
    Just a band-aid for Django-nonrel on AppEngine.
    """
    def open(img_data):
        """
        Static factory method.  
        On upload, via django-nonrel/GAE, img_data is cStringIO instance.
        """
        try:
            return Image.__instances[img_data]
        except KeyError:
            instance = Image()
            instance._logger = logging.getLogger(__name__)
            instance._logger.debug('Fake-PIL open(%s)', img_data)
            instance._img_data = img_data
            instance._img_bytes = None
            instance._img_len = None
            Image.__instances[img_data] = instance
            return instance

    open = staticmethod(open)

    def load(self):
        """
        Read image data into memory.
        """
        if hasattr(self._img_data, 'read'):
            self._img_bytes = self._img_data.read()
        else: 
            # don't know if we need this...
            self._img_bytes = self._img_data['content']

        if self._img_bytes is None:
            self.logger.debug('Fake-PIL No data for image')
            raise Exception('No data for image')

        self._img_len = len(self._img_bytes)
        self._logger.debug('Fake-PIL read %d bytes', self._img_len)

        if self._img_len < 0:
            self.logger.debug('Fake-PIL No data (len=%d) for image', self._img_len)
            raise Exception('No data for image (len=%d)' % self._img_len)            

    def verify(self):
        if self._img_len > 0:
            self._logger.debug('Fake-PIL testing images.Image(len=%d bytes)', self._img_len)
            test_img = images.Image(self._img_bytes)
            # Histogram will throw an exception if it fails, triggering django validation
            ignored_output = test_img.histogram()
        else:
            self._logger.warn('Fake-PIL has no bytes.  Why would this be valid?')

