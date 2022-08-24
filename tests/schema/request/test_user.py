"""
Unit tests for schema.request.user
"""

import unittest
from unittest.mock import patch, MagicMock

from resource_allocator.schemas.request import user

class RegisterUserRequestSchemaTestCase(unittest.TestCase):
    def setUp(self):
        self.valid_user = {
            "email": "some@example.com",
            "password": "1234Aa.",
            "first_name": "bla",
            "last_name": "bla",
        }
        self.invalid_user = {
            "email": "not an email",
            "password": "-",
            "first_name": 12,
            "last_name": 12,
        }
        self.dupe_user = {
            "email": "dupe_user@example.com",
            "password": "1234Aa.",
            "first_name": "bla",
            "last_name": "bla",
        }

    @patch("resource_allocator.schemas.request.user.sess")
    def test_register_user_schema(self, mock_sess: MagicMock):
        mock_sess.query.return_value.all.return_value = [("dupe_user@example.com", )]
        schema = user.RegisterUserRequestSchema()

        with self.subTest("valid user"):
            errors = schema.validate(self.valid_user)
            self.assertEqual(len(errors), 0)

        with self.subTest("Invalid user"):
            result = schema.validate(self.invalid_user)
            self.assertEqual(len(result), 4)
            self.assertIn("email", result.keys())
            self.assertIn("Not a valid email address", result["email"][0])
            self.assertIn("password", result.keys())
            self.assertIn("Invalid password", result["password"][0])

        with self.subTest("Dupe user"):
            result = schema.validate(self.dupe_user)
            self.assertIn("email", result.keys())
            self.assertNotIn("password", result.keys())
            self.assertIn("already registered", result["email"][0])


class LoginUserRequestSchemaTestCase(unittest.TestCase):
    def setUp(self):
        self.valid_user = {
            "email": "some@example.com",
            "password": "1234Aa.",
        }
        self.invalid_user = {
            "bla": 12,
        }

    def test_login_user_request_schema(self):
        schema = user.LoginUserRequestSchema()

        with self.subTest("valid user"):
            result = schema.validate(self.valid_user)
            self.assertEqual(len(result), 0)

        with self.subTest("Invalid user"):
            result = schema.validate(self.invalid_user)
            self.assertEqual(len(result), 3)
            self.assertIn("email", result.keys())
            self.assertIn("password", result.keys())
            self.assertIn("bla", result.keys())
            self.assertIn("Unknown field", result["bla"][0])

