"""
Unit tests for utils.auth
"""

import datetime as dt
import unittest
from unittest.mock import patch, MagicMock

from resource_allocator.utils import auth

class GenerateTokenTestCase(unittest.TestCase):
    def setUp(self):
        self.secret = "some_secret"
        self.id = 12

    def test_generate_token(self):
        token = auth.generate_token(id = self.id, secret = self.secret)
        self.assertTrue(isinstance(token, str))
        self.assertGreater(len(token), 0)


class ValidateTokenTestCase(unittest.TestCase):
    def setUp(self):
        self.secret = "some_secret"
        self.id = 12

    def test_validate_token(self):
        #   NOTE: this depends on utils.auth.generate_token
        token = auth.generate_token(id = self.id, secret = self.secret)
        parsed_token = auth.parse_token(token, secret = self.secret)
        self.assertLessEqual(set(["iat", "exp", "sub"]), set(parsed_token.keys()))
        self.assertEqual(parsed_token["sub"], self.id)

    def test_expired_token(self):
        token = auth.generate_token(
            id = self.id,
            secret = self.secret,
            now = dt.datetime(2000, 1, 1),
        )
        fun = lambda: auth.parse_token(token = token, secret = self.secret)
        self.assertRaises(auth.jwt.ExpiredSignatureError, fun)

