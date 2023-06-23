"""
Test for the db module
"""

import unittest

import sqlalchemy

from resource_allocator.config import Config
from resource_allocator.db import get_session


class GetSessionTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Config.from_environment()

    def test_get_session(self):
        sess = get_session()

        self.assertTrue(isinstance(sess, sqlalchemy.orm.Session))
        
        #   Test injection
        self.assertIsNotNone(self.config._sess)
        self.assertTrue(sess is self.config._sess)

        #   New session is the same session
        new_sess = get_session()
        self.assertTrue(sess is new_sess)
