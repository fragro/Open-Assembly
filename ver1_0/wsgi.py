import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(os.path.dirname('openassembly/')))))
print sys.path

from django.core.handlers.wsgi import WSGIHandler
os.environ["DJANGO_SETTINGS_MODULE"] = "openassembly.settings"
application = WSGIHandler()
