"""Checkouts application middleware"""

import logging
import time

logger = logging.getLogger('analytics')

class Analytics():
    """Tracks request details useful for analysis of usage patterns.
    
    To ensure that the name of the logged in user can be accessed, this
    middleware should come after Django's built-in AuthenticationMiddleware
    in the project settings.
    """
    
    def collect_request_details(self, request):
        """Gathers information of interest from the request and returns a dictionary."""
        context = {
            'ip':        request.META['REMOTE_ADDR'],
            'method':    request.method,
            'path':      request.path,
            'user':      request.user.username,
            'useragent': request.META['HTTP_USER_AGENT'],
        }
        
        # Fall-back if the user is not recognized
        if not request.user.is_authenticated():
            context['user'] = 'anonymous'
        
        return context
    
    def process_request(self, request):
        """Captures the current time and saves it to the request object."""
        request._analytics_start_time = time.time()
    
    def process_response(self, request, response):
        """Organizes info from each request/response and saves it to a log."""
        context = self.collect_request_details(request)
        context['status'] = response.status_code
        
        if not request._analytics_start_time:
            logger.error("Unable to provide timing data for request")
            context['elapsed'] = -1.0
        else:
            elapsed = (time.time() - request._analytics_start_time) * 1000.0
            context['elapsed'] = elapsed
        
        template = "%(user)s@%(ip)s: %(method)s %(path)s %(elapsed)fms %(status)s \"%(useragent)s\""
        logger.info(template % context)
        
        return response
