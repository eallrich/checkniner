"""Checkouts application middleware"""

import logging

logger = logging.getLogger('analytics')

class Analytics():
    """Tracks request details useful for analysis of usage patterns.
    
    To ensure that the name of the logged in user can be accessed, this
    middleware should come after Django's built-in AuthenticationMiddleware
    in the project settings.
    """
    
    def process_request(self, request):
        """Organizes info from each request and saves it to a log."""
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
        
        template = "%(user)s@%(ip)s: %(method)s %(path)s \"%(useragent)s\""
        logger.info(template % context)
