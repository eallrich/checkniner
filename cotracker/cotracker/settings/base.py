# Common settings

import os

from django.core.exceptions import ImproperlyConfigured

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# From checkniner/cotracker/cotracker/settings/base.py to checkniner/cotracker/
PROJECT_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir)

LOGS_PATH = os.path.join(PROJECT_ROOT, 'logs')
if not os.path.isdir(LOGS_PATH):
    os.mkdir(LOGS_PATH)


def get_env_var(name):
    """Attempts to retrieve the named environment variable. If the name does
    not exist in the environment, an exception is raised."""
    
    try:
        return os.environ[name]
    except KeyError:
        error_message = "The '%s' environment variable is not set" % name
        raise ImproperlyConfigured(error_message)

if get_env_var('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(),
    }

sentry_sdk.init(
    dsn=get_env_var('SENTRY_DSN'),
    integrations=[DjangoIntegration()]
)

PILOTWEIGHTS_JSON_FILE = get_env_var('EXPORT_PREFIX') + '_pilotweights.json'
PILOTWEIGHTS_XML_FILE =  get_env_var('EXPORT_PREFIX') + '_pilotweights.xml'

# If the user has defined this env var, we're going to assume that they also
# defined the rest of the env vars needed for sending email. If this env var
# is missing, we're going to (silently) assume that they don't want to use
# the email notification system.
if 'MAILGUN_SENDER' in os.environ:
    MAILGUN_CONFIG = {
        'from': get_env_var('MAILGUN_SENDER'),
        'api_url': get_env_var('MAILGUN_API_URL'),
        'api_key': get_env_var('MAILGUN_API_KEY'),
        'send_weight_notify_to':  get_env_var('NOTIFY_WEIGHT_TO'),
        'send_weight_notify_cc':  os.getenv('NOTIFY_WEIGHT_CC', None),
        'send_weight_notify_bcc': os.getenv('NOTIFY_WEIGHT_BCC', None),
    }
else:
    MAILGUN_CONFIG = None

LOGIN_URL = '/login/'
# Default 'successful login' URL redirect if an alternative is not specified
LOGIN_REDIRECT_URL = '/checkouts/'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Make this unique, and don't share it with anybody.
SECRET_KEY = get_env_var('SECRET_KEY')

MIDDLEWARE = (
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'checkouts.middleware.Analytics',
)

ROOT_URLCONF = 'cotracker.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'cotracker.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_ROOT, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'checkouts',
)

main_header = '='*100
sub_header = '-'*100
verbose_format = main_header + "\n%(asctime)s [%(process)s] [%(levelname)s] (%(status_code)s) %(message)s\n" + sub_header + "\n%(request)s"
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose_request': {
            'format': verbose_format,
        },
        'checkouts_log': {
            'format': '%(asctime)s | [%(process)s] [%(levelname)s] %(message)s',
        },
        'checkouts_console': {
            'format': '[%(process)s] [%(levelname)s] %(message)s',
        },
        'analytics_log': {
            'format': '%(asctime)s [%(process)s]: at=%(levelname)s %(message)s',
            'datefmt': "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    'handlers': {
        'logfile_requests': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'requests.log'),
            'formatter': 'verbose_request',
        },
        'logfile_checkouts': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'checkouts.log'),
            'formatter': 'checkouts_log',
        },
        'console_checkouts': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'checkouts_console',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'logfile_analytics': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'analytics.log'),
            'formatter': 'analytics_log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['logfile_requests', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'checkouts': {
            'handlers': ['logfile_checkouts', 'console_checkouts'],
            'level': 'INFO',
            'propagate': True,
        },
        'analytics': {
            'handlers': ['logfile_analytics',],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
