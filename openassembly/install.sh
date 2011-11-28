#!/bin/bash

MANAGE=`ls manage.py`
SETTINGS=`ls settings.py`
if [ $MANAGE != "manage.py" -o $SETTINGS != "settings.py" ]; then
  echo "This script should only be executed inside the openassembly project directory."
  exit
fi

LIB=`ls ../ | grep lib`
DJANGO=`ls | grep -E 'djangoappengine|djangotoolbox|native_tags|piston|dselector.py'`

if [ -z "$LIB" -a -z "$DJANGO" ]; then
  # remember where you started
  HERE=`pwd`

  # create the lib directory
  cd ../
  mkdir lib
  cd lib

  # grab all of the dependencies
  hg clone http://bitbucket.org/wkornewald/djangoappengine/
  hg clone http://bitbucket.org/wkornewald/django-nonrel/
  hg clone http://bitbucket.org/wkornewald/djangotoolbox/
  hg clone http://bitbucket.org/legutierr/django-customtags-lib/
  hg clone http://bitbucket.org/legutierr/django-tagging-multidb/
  hg clone http://bitbucket.org/offline/django-annoying/
  hg clone http://bitbucket.org/jmoiron/django-selector/
  hg clone http://bitbucket.org/fragro/markdown
  hg clone http://bitbucket.org/fragro/beautifulsoup
  hg clone http://bitbucket.org/twanschik/django-autoload
  hg clone http://bitbucket.org/wkornewald/django-dbindexer
  hg clone http://bitbucket.org/wkornewald/django-filetransfers 
  hg clone http://bitbucket.org/fragro/python-oauth
  hg clone http://bitbucket.org/fragro/python-httplib2
  hg clone http://bitbucket.org/fragro/python-openid
  hg clone http://bitbucket.org/carljm/django-markitup
  hg clone http://bitbucket.org/fragro/simplebox
  git clone http://github.com/facebook/python-sdk.git
  git clone http://github.com/flashingpumpkin/django-socialregistration.git
  hg clone http://bitbucket.org/twanschik/nonrel-search
  svn checkout http://minidetector.googlecode.com/svn/trunk/ minidetector-read-only
  git clone https://github.com/johnyma22/etherpad-lite-jquery-plugin.git
  git clone https://github.com/devjones/PyEtherpadLite.git

  # go back to where you started
  cd $HERE

  # create the required symbolic links

  ln -s ../lib/python-httplib2/httplib2-0.6.0/python2/httplib2
  ln -s ../lib/python-oauth/oauth2-1.5.170/oauth2
  ln -s ../lib/python-openid/python-openid-2.2.5/openid
  ln -s ../lib/django-markitup/markitup
  ln -s ../lib/django-filetransfers/filetransfers
  ln -s ../lib/django-autoload/autoload 
  ln -s ../lib/django-dbindexer/dbindexer
  ln -s ../lib/djangoappengine
  ln -s ../lib/django-nonrel/django
  ln -s ../lib/djangotoolbox/djangotoolbox
  ln -s ../lib/django-customtags-lib/customtags
  ln -s ../lib/django-tagging-multidb/tagging
  ln -s ../lib/django-annoying/annoying
  ln -s ../lib/django-selector/dselector.py
  ln -s ../lib/markdown/python-markdown/markdown
  ln -s ../lib/beautifulsoup/BeautifulSoup.py
  ln -s ../lib/django-socialregistration/socialregistration 
  ln -s ../lib/python-sdk/src/facebook.py
  ln -s ../lib/nonrel-search/search
  ln -s ../lib/minidetector-read-only/minidetector
  ln -s ../lib/PyEtherpadLite/src/py_etherpad.py

  # add static symbolic links
  cd static
  ln -s ../../lib/simplebox
  ln -s ../../lib/django-markitup/markitup/static/markitup
  cd js
  ln -s ../..../lib/etherpad-lite-jquery-plugin/js/etherpad.js 
  cd ../../

  # add the app.yaml file
  cp app.yaml.example app.yaml

  # run syncdb
  python manage.py syncdb

fi
