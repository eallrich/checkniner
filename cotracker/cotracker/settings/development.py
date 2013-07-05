from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

INSTALLED_APPS += ('debug_toolbar',)

INTERNAL_IPS = tuple(get_env_var('INTERNAL_IPS').split(','))

LOGGING['loggers']['django.request']['level'] = 'DEBUG'
LOGGING['loggers']['checkouts']['level'] = 'DEBUG'
LOGGING['loggers']['analytics']['level'] = 'DEBUG'
