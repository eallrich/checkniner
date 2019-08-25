"""Checkouts application middleware"""

import datetime
import logging
import subprocess
import time

from django.contrib import messages

logger = logging.getLogger('analytics')

class Analytics():
    """Tracks request details useful for analysis of usage patterns.

    To ensure that the name of the logged in user can be accessed, this
    middleware should come after Django's built-in AuthenticationMiddleware
    in the project settings.
    """
    def __init__(self, get_response):
        self.get_response = get_response


    def is_monitor_agent(self, request):
        """Returns True if this request is related to a known monitoring agent."""
        keywords = [
            'UptimeRobot', # Nifty free service
        ]

        useragent = request.META.get('HTTP_USER_AGENT', None)
        if useragent is None:
            return False # Can't recognize a blank useragent

        for word in keywords:
            if word in useragent:
                return True
        return False


    def get_queue_start(self, request):
        """Returns the timestamp this request started (as reported by downstream)"""
        try:
            header = request.META['HTTP_X_REQUEST_START'] # must be set by nginx
        except KeyError:
            return 0 # Header wasn't provided by reverse proxy
        value = float(header[2:]) # discard 't=' prefix
        return value


    def collect_request_details(self, request):
        """Gathers information of interest from the request and returns a dictionary."""
        # Use the REMOTE_ADDR if we have it. If not, Nginx is configured to
        # set both X-Real-IP and X-Forwarded-For; pick one of those instead.
        client_ip = request.META['REMOTE_ADDR']
        if client_ip == '':
            client_ip = request.META['HTTP_X_REAL_IP']

        try:
            queue_time = request._queue_time
        except AttributeError:
            queue_time = 0

        context = {
            'ip':        client_ip,
            'method':    request.method,
            'path':      request.path,
            'queue':     queue_time,
            'useragent': request.META.get('HTTP_USER_AGENT', 'None'),
        }

        if hasattr(request, 'user') and request.user.is_authenticated():
            context['user'] = request.user.username
        else:
            context['user'] = 'anonymous'

        return context


    def process_request(self, request):
        """Captures the current time and saves it to the request object."""
        if self.is_monitor_agent(request):
            return # No metrics
        now = time.time()
        request._analytics_start_time = now
        try:
            request._queue_time = (now - self.get_queue_start(request)) * 1000.0
        except AttributeError:
            pass # Nothing to do, no queue time to report


    def process_response(self, request, response):
        """Organizes info from each request/response and saves it to a log."""
        if self.is_monitor_agent(request):
            return response # No metrics, no logging

        context = self.collect_request_details(request)
        context['status'] = response.status_code
        context['bytes'] = len(response.content)

        if hasattr(request, '_analytics_start_time'):
            elapsed = (time.time() - request._analytics_start_time) * 1000.0
            context['elapsed'] = elapsed
        else:
            context['elapsed'] = -1.0

        template = "client=%(user)s@%(ip)s method=%(method)s path=%(path)s queue=%(queue).0fms real=%(elapsed).0fms status=%(status)s bytes=%(bytes)s useragent=\"%(useragent)s\""
        logger.info(template % context)

        return response


    def current_django(self):
        with open('/home/checkniner/checkniner/requirements/base.txt', 'r') as f:
            line = f.readline()
            if 'Django==' in line:
                return line.split('==')[-1].strip()


    def available_django(self, series):
        logger.info("Checking for latest django in series=%s" % series)
        channel = subprocess.run(
            ['pip', 'install', 'Django==999'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        text = channel.stdout.decode('utf-8').replace(',', '')
        return [v for v in text.split(' ') if v.startswith(series)][-1].strip()


    def update_check(self, request):
        django_1_11_eol = datetime.date(2020, 4, 30)
        if datetime.date.today() > django_1_11_eol:
            m = 'You are using Django 1.11 which is no longer supported and has security vulnerabilities. Upgrade immediately.'
            messages.error(request, m)
            return

        have_django = self.current_django()
        want_django = self.available_django(have_django.rsplit('.', 1)[0])
        logger.info("Have django=%s, want django=%s" % (have_django, want_django))
        if want_django > have_django:
            m = 'You are using Django %s. A security update to Django %s is available. Upgrade to mitigate attacks.'
            messages.warning(request, m % (have_django, want_django))


    def __call__(self, request):
        self.process_request(request)
        #if request.user and request.user.is_authenticated() \
        #   and 'logout' not in request.path \
        #   and 'password_change' not in request.path \
        #   and request.path != '/':
        #    try:
        #        self.update_check(request)
        #    except:
        #        logger.exception("Encountered an error during update_check middleware, skipping")
        response = self.get_response(request)
        return self.process_response(request, response)
