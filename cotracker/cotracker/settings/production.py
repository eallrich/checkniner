from .base import *

if bool(os.environ.get('FORCE_DEBUG_MODE')):
    DEBUG = True
else:
    DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

ALLOWED_HOSTS = [get_env_var('ALLOWED_HOST'),]
