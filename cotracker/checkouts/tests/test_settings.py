import os
# We want to test the utility functions in the settings
# module, not the settings themselves, so we'll use 
# unittest directly (instead of importing django.test)
import unittest

from django.core.exceptions import ImproperlyConfigured

from cotracker.settings import base

class SettingsTests(unittest.TestCase):
    
    def setUp(self):
        self.success_key = 'TEST_RANDOM_KEY_EXISTS'
        self.failure_key = 'TEST_RANDOM_KEY_MISSING'
        
        os.environ[self.success_key] = self.success_key
    
    def test_get_env_var_success(self):
        self.assertEqual(base.get_env_var(self.success_key), self.success_key)
    
    def test_get_env_var_failure(self):
        self.assertRaises(ImproperlyConfigured, base.get_env_var, self.failure_key)
    
    def tearDown(self):
        os.environ.pop(self.success_key)
