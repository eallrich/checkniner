"""Checkouts application middleware"""

import logging

from django.contrib.auth.models import User
from django.core.exceptions import MiddlewareNotUsed

import util

logger = logging.getLogger(__name__)

class UserIsPilotPatch():
    """Patches the django built-in user model with a method for determining
    whether the user is a member of the 'Pilots' group.
    
    Because we only need to patch the model once (when an interpreter begins)
    we can make use of the __init__ method: This method is called just once
    for middleware, when the interpreter responds to the first request. [0]
    Once the User model is patched, we can completely remove ourselves from the
    middleware process by raising MiddlewareNotUsed. [1]
    
    [0] https://docs.djangoproject.com/en/1.5/topics/http/middleware/#init
    [1] https://docs.djangoproject.com/en/1.5/topics/http/middleware/#marking-middleware-as-unused
    """
    
    def __init__(self):
	"""Adds a method, is_pilot(self), to the built-in User model.
	
	util.is_pilot expects a single argument, the User instance to check.
	Since we're intending to use is_pilot as a bound method on User
	instances, we can let the inherent 'self' argument be passed directly
	to util.is_pilot:
	>>> foo = User.objects.get(pk=1)
	>>> foo.is_pilot() # foo.is_pilot(self), becomes util.is_pilot(foo)
	"""
	logger.info("Patching built-in User model with 'is_pilot()'")
	User.is_pilot = util.is_pilot
	
	# We're not interested in seeing future requests/responses, so let 
	# Django know that we can be disabled.
	logger.debug("Removing 'UserIsPilotPatch' from the middleware process")
	raise MiddlewareNotUsed()