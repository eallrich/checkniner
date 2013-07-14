import datetime
import importlib
import logging
import os

import dj_database_url
import envoy

logging.basicConfig(
    filename='collect.log',
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
logger = logging.getLogger(__name__)

# Would be '[]' without the '--indent=4' argument to dumpdata
EMPTY_FIXTURE = '[\n]\n'

def capture_command(function):
    def wrapper(*args, **kwargs):
        if args:
            logger.info(args[0])
        elif 'command' in kwargs:
            logger.info(kwargs['command'])
        else:
            logger.warning('Unknown command.\n\targs: %r\n\tkwargs: %r' % (args, kwargs))
        
        return function(*args, **kwargs)
    return wrapper

def instrument(function):
    def wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        r = function(*args, **kwargs)
        end = datetime.datetime.now() - start
        milliseconds = end.microseconds / 1000
        logger.debug("    real=%dms" % milliseconds)
        return r
    return wrapper

# Keep a log of the calls through envoy
envoy.run = instrument(capture_command(envoy.run))

def get_database_name(env='DATABASE_URL'):
    db_config = dj_database_url.config(env)
    return db_config['NAME']

def get_django_settings(env='DJANGO_SETTINGS_MODULE'):
    name = os.environ.get(env)
    return importlib.import_module(name)

def get_installed_app_names():
    settings = get_django_settings()
    apps = settings.INSTALLED_APPS
    # E.g. 'django.contrib.auth' -> 'auth'
    names = [n.split('.')[-1] for n in apps]
    return names

def dump_postgres():
    database = get_database_name()
    r = envoy.run("pg_dump %s" % database)
    with open("%s.sql" % database, 'wb') as f:
        f.write(r.std_out)
    
def dump_django_fixtures():
    for name in get_installed_app_names():
        r = envoy.run('django-admin.py dumpdata %s --indent=4' % name)
        if r.std_out != EMPTY_FIXTURE:
            with open('%s.json' % name, 'wb') as f:
                f.write(r.std_out)
        else:
            logger.warning("Skipping empty fixture for '%s'" % name)

logger.info("Beginning collection of backup data")
dump_postgres()
dump_django_fixtures()
logger.info("Collection complete")
