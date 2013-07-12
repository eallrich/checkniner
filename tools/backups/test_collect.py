import os
from unittest import TestCase

import collect

class TestEnvironment(TestCase):
    
    def setUp(self):
        self.db_env = 'TEST_DATABASE_URL'
        db_url = 'postgres://ubuntu@/checkniner'
        os.environ[self.db_env] = db_url
    
    def test_find_database_name(self):
        db_name = collect.get_database_name(env=self.db_env)
        self.assertEqual(db_name, 'checkniner')
    
    def tearDown(self):
        os.environ.pop(self.db_env)

