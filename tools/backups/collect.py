import datetime
import hashlib
import importlib
import logging
import os
import tarfile

import dj_database_url
import envoy

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

# Would be '[]' without the '--indent=4' argument to dumpdata
EMPTY_FIXTURE = '[\n]\n'

logging.basicConfig(
    filename='collect.log',
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt=DATE_FORMAT,
)
logger = logging.getLogger(__name__)

def instrument(function):
    def wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        r = function(*args, **kwargs)
        end = datetime.datetime.now() - start
        milliseconds = end.microseconds / 1000
        return (milliseconds, r)
    return wrapper

def capture_command(function):
    def wrapper(*args, **kwargs):
        if args:
            command = args[0]
        elif 'command' in kwargs:
            command = kwargs['command']
        else:
            logger.warning("What's the command?.\n\targs: %r\n\tkwargs: %r" % (args, kwargs))
            command = '?'
        
        # Being much too clever: Dynamically decorate the given function with
        # the 'instrument' function so that we can capture timing data. Once
        # it's decorated, we'll call the original function with the original
        # parameters.
        milliseconds, r = instrument(function)(*args, **kwargs)
        bytes = len(r.std_out)
        logger.info("cmd=\"%s\" real=%dms bytes=%d" % (command, milliseconds, bytes))
        if hasattr(r, 'std_err'):
            # Print each non-blank line separately
            lines = [line for line in r.std_err.split('\n') if line]
            map(logger.error, lines)
        return r
    return wrapper

def capture_function(function):
    def wrapper(*args, **kwargs):
        milliseconds, r = instrument(function)(*args, **kwargs)
        logger.info("func=\"%s\" real=%dms" % (function.__name__, milliseconds))
        if hasattr(r, 'std_err'):
            # Print each non-blank line separately
            lines = [line for line in r.std_err.split('\n') if line]
            map(logger.error, lines)
        return r
    return wrapper

# Keep a log of the calls through envoy
envoy.run = capture_command(envoy.run)

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
    filename = "%s.sql" % database
    with open(filename, 'wb') as f:
        f.write(r.std_out)
    return filename
    
def dump_django_fixtures():
    filenames = []
    for name in get_installed_app_names():
        r = envoy.run('django-admin.py dumpdata %s --indent=4' % name)
        if r.std_out != EMPTY_FIXTURE:
            filename = "%s.json" % name
            with open(filename, 'wb') as f:
                f.write(r.std_out)
            filenames.append(filename)
        else:
            logger.warning("Skipping empty fixture for '%s'" % name)
    return filenames

def sha1sum(file):
    m = hashlib.sha1()
    try:
        logger.debug("Treating '%s' as an open file" % file)
        m.update(file.read())
    except AttributeError:
        logger.debug("Now trying '%s' as a file path" % file)
        with open(file, 'rb') as f:
            m.update(f.read())
    return m.hexdigest()

@capture_function
def update_necessary():
    latest = 'latest.tar.gz'
    # Shortcut if we have nothing to compare against (e.g. the first run)
    if not os.path.exists(latest):
        logger.debug("Could not access '%s', assuming first run" % latest)
        return True
    to_compare = ('auth.json', 'checkouts.json')
    for name in to_compare:
        proposed = sha1sum(name)
        with tarfile.open(latest, 'r:gz') as tar:
            for tarinfo in tar:
                if tarinfo.name == name:
                    original = sha1sum(tar.extractfile(tarinfo))
                    logger.debug("Was %s, now %s" % (original, proposed))
    return False

@capture_function
def package(filenames):
    logger.info("Packaging archive")
    logger.debug("Contents: %s" % filenames)
    date = datetime.datetime.now().strftime(DATE_FORMAT)
    filename = "%s.tar.gz" % date
    with tarfile.open(filename, 'w:gz') as archive:
        map(archive.add, filenames)
    os.symlink(filename, 'latest.tar.gz')
    return filename

filenames = [dump_postgres(),]
filenames.extend(dump_django_fixtures())
if update_necessary():
    archive = package(filenames)
    archive_size = os.path.getsize(archive)
    logger.info("---- Archiving complete ---- bytes=%d --------------------" % archive_size)
map(os.remove, filenames)
