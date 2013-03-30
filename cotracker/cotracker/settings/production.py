from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

ALLOWED_HOSTS = [get_env_var('ALLOWED_HOST'),]
