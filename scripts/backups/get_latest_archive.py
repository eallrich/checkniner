import datetime
import logging
import os

from boto.s3.connection import S3Connection
from boto.s3.bucket import Bucket
from boto.s3.key import Key


# ISO 8601 YYYY-MM-DDTHH:MM:SS
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


logging.basicConfig(
    filename='retrieve.log',
    level=logging.INFO,
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


def capture_function(function):
    def wrapper(*args, **kwargs):
        milliseconds, r = instrument(function)(*args, **kwargs)
        logger.info("func=\"%s\" real=%dms" % (function.__name__, milliseconds))
        return r
    return wrapper


def get_s3_credentials():
    access = os.environ['S3_ACCESS_KEY']
    secret = os.environ['S3_SECRET_KEY']
    return (access, secret)


def get_s3_bucket_name():
    return os.environ['S3_BUCKET_NAME']


@capture_function
def get_latest_key(bucket, key_prefix, delimiter='/', max_day_range=1):
    latest_key = None
    datefmt = DATE_FORMAT.split('T')[0]
    date = datetime.date.today()
    date_limit = date - datetime.timedelta(days=max_day_range)
    logger.info("Checking dates between %s and %s" % (date.strftime(datefmt), date_limit.strftime(datefmt)))
    
    while date >= date_limit:
        prefix = delimiter.join([key_prefix, date.strftime(datefmt)])
        logger.info("Looking up '%s'" % prefix)
        matched = bucket.list(prefix=prefix, delimiter=delimiter)
        # We can't jump straight to the end of the iterator, but we can iterate
        # over a (fairly small) set reasonably efficiently. If we save each key
        # as we come across it, assuming the keys are ordered, then the last
        # key we save will be the latest.
        for key in matched:
            latest_key = key
        
        if latest_key is not None:
            logger.info("Found a match with '%s'" % (latest_key.key))
            return latest_key
        else:
            # No luck on the current day, try the previous one
            date = date - datetime.timedelta(days=1)
    logger.info("Unable to find a matching key newer than %s" % (date_limit.strftime(datefmt)))
    return None


@capture_function
def download():
    latest = 'latest.tar.gz'
    access, secret = get_s3_credentials()
    connection = S3Connection(access, secret)
    
    bucket_name = get_s3_bucket_name()
    bucket = Bucket(connection, bucket_name)
    
    key_prefix = 'db'
    key = get_latest_key(bucket, key_prefix)
    if key is None:
        logger.warning("Unable to locate latest archive on S3")
    else:
        key.get_contents_to_filename(latest)


download()
