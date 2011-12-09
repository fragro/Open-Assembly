#from djangoappengine.settings_base import *
import os
import json

FACEBOOK_API_KEY = ''
FACEBOOK_APP_ID = ''
FACEBOOK_SECRET_KEY = ''

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET_KEY = ''
TWITTER_REQUEST_TOKEN_URL = ''
TWITTER_ACCESS_TOKEN_URL = ''
TWITTER_AUTHORIZATION_URL = ''

SECRET_KEY = '=r-$b*8hglm+858&9t043hlm6-&6-3d3vfc4((7yd0dbrakhvi'
try:
    ###IF DEPLOYING ON DOTCLOUD THIS WILL SUCCEED
    with open(os.path.expanduser('~/environment.json')) as f:
        env = json.load(f)

    DEBUG = True
    TEMPLATE_DEBUG = DEBUG

    DATABASES = {
        'default': {
            'ENGINE': 'django_mongodb_engine',
            'NAME': 'admin',
            'HOST': env['DOTCLOUD_DB_MONGODB_URL'],
            'SUPPORTS_TRANSACTIONS': False,
        }
    }

    STATICFILES_DIRS = (
        "/home/dotcloud/current/openassembly/static/",
    )
    MEDIA_ROOT = '/home/dotcloud/data/media/'
    STATIC_ROOT = '/home/dotcloud/data/static/'
    MEDIA_URL = '/media/'
except:

    DEBUG = True
    TEMPLATE_DEBUG = DEBUG

    ADMINS = (('Frank', 'fragro@gmail.com'),)

    MANAGERS = ADMINS

    DATABASES = {
        'default': {
            'ENGINE': 'django_mongodb_engine',
            'NAME': 'admin'
        }
    }
    STATICFILES_DIRS = (
        "static/",
    )
    STATIC_ROOT = 'static_dev_serve/static/'
    MEDIA_ROOT = 'static_dev_serve/media/'
    MEDIA_URL = '/media/'

ADMINS = (('Frank', 'fragro@gmail.com'),)

MANAGERS = ADMINS

AUTOLOAD_SITECONF = 'indexes'

INSTALLED_APPS = (
    'dbindexer',
    'autoload',
    'djangotoolbox',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.markup',
    'customtags',
    'tagging',
    'filetransfers',
    'pirate_core',
    'pirate_issues',
    'pirate_deliberation',
    'pirate_permissions',
    'pirate_ranking',
    'pirate_consensus',
    'pirate_reputation',
    'pirate_messages',
    'pirate_login',
    'pirate_profile',
    'pirate_sources',
    'pirate_comments',
    'pirate_badges',
    'pirate_flags',
    'pirate_social',
    'pirate_forum',
    'pirate_actions',
    'pirate_topics',
    'markitup',
    'oa_verification',
    'oa_filmgenome',
    'notification',
    'search',
    'oa_suggest',
    'oa_platform',
    'oa_cache',
    'django_mongodb_engine'
)

STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

MARKITUP_MEDIA_URL = '/static/'

MARKITUP_FILTER = ('markdown.markdown', {'safe_mode': True, 'previewParserPath': '/markitup/preview/'})
MARKITUP_SET = 'markitup/sets/markdown'
MARKITUP_SKIN = 'simple'

JQUERY_URL = '/static/jquery-1.4.2.min.js'

DOMAIN_NAME = 'www.openassembly.org'

SERVER_EMAIL = 'fragro@gmail.com'

DEFAULT_FROM_EMAIL = 'fragro@gmail.com'

TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)

FAIL_SILENTLY = True

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

DJANGO_BUILTIN_TAGS = (
    'native_tags.templatetags.native',
    'django.contrib.markup.templatetags.markup',
)

MIDDLEWARE_CLASSES = (
    'autoload.middleware.AutoloadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'pirate_core.middleware.UrlMiddleware',
    'customtags.middleware.AddToBuiltinsMiddleware',
    'minidetector.middleware.MobileMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

SEARCH_BACKEND = 'search.backends.immediate_update'
PISTON_DISPLAY_ERRORS = True

OPENASSEMBLY_AGENT = 'http://localhost:8888/jsonrpc'
OPENASSEMBLY_KEY = "frank"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
