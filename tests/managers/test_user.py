"""
Tests for the managers.auth module
"""

import datetime as dt
import unittest
from unittest.mock import patch, MagicMock

import jwt

from resource_allocator import models
from resource_allocator.config import SECRET
from resource_allocator.db import engine, sess
from resource_allocator.main import create_app
from resource_allocator.managers import user
from resource_allocator.utils.db import change_schema

metadata = change_schema(models.metadata, schema = "resource_allocator_test")

class UserManagerTestCase(unittest.TestCase):
    def setUp(self):
        metadata.create_all(engine)
        models.populate_enums(metadata, sess)
        self.data = {
            "email": "test@example.com",
            "password": 123456,
            "first_name": "bla",
            "last_name": "bla",
        }
        self.azure_response = {
            "mail": self.data["email"],
            "givenName": self.data["first_name"],
            "surname": self.data["last_name"],
        }

    def tearDown(self):
        sess.rollback()
        metadata.drop_all(bind = engine)

    def test_register(self):
        result = user.UserManager.register(self.data)
        self.assertTrue(isinstance(result, dict))
        self.assertIn("token", result.keys())

        users = sess.query(models.UserModel).all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, self.data["email"])
        self.assertNotEqual(users[0].password_hash, self.data["password"])
        self.assertIsNotNone(users[0].role_id)

    def test_login(self):
        registration = user.UserManager.register(self.data)
        result = user.UserManager.login(self.data)
        self.assertTrue(isinstance(result, dict))
        self.assertIn("token", result.keys())

    def test_login_invalid_password(self):
        registration = user.UserManager.register(self.data)
        result = user.UserManager.login({**self.data, "password": "invalid_pass"})
        self.assertIn("Invalid password", result)

    def test_login_invalid_user(self):
        registration = user.UserManager.register(self.data)
        result = user.UserManager.login({**self.data, "email": "bla@example.com"})
        self.assertIn("No such user", result[0]) # message

    def test_register_azure(self):
        result = user.UserManager._register_azure(self.azure_response)
        self.assertTrue(isinstance(result, models.UserModel))

        users = sess.query(models.UserModel).all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, self.data["email"])
        self.assertIsNone(users[0].password_hash)
        self.assertIsNotNone(users[0].role_id)
        self.assertTrue(users[0].is_external)

    @patch("resource_allocator.managers.user.get_azure_user_info")
    @patch("resource_allocator.managers.user.req.session")
    def test_login_azure_finish(self, req_session: MagicMock, get_azure_user_info: MagicMock):
        auth_response = MagicMock()
        auth_response.send.return_value.ok = True
        auth_response.send.return_value.json.return_value = {"access_token": "access_token"}
        req_session.__enter__.return_value = auth_response
        get_azure_user_info.return_value = self.azure_response

        result = user.UserManager.login_azure_finish(data = {"code": "some_code"})
        self.assertTrue(isinstance(result, dict))
        self.assertIn("token", result.keys())

        users = sess.query(models.UserModel).all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, self.data["email"])
        self.assertIsNone(users[0].password_hash)
        self.assertIsNotNone(users[0].role_id)
        self.assertTrue(users[0].is_external)


class VerifyTokenTestCase(unittest.TestCase):
    def setUp(self):
        now = dt.datetime.utcnow()
        self.data = {
            "sub": 12,
            "iat": now,
            "exp": now + dt.timedelta(seconds = 3600),
        }
        self.good_token = jwt.encode(self.data, key = SECRET, algorithm = "HS256")

        self.expired_token = jwt.encode({
            **self.data,
            "exp": 0,
        }, key = SECRET, algorithm = "HS256")

    @patch("resource_allocator.managers.user.sess")
    def test_verify_token(self, mock_sess: MagicMock):
        with self.subTest("Good token"):
            mock_sess.get.return_value = 12
            result = user.verify_token(self.good_token)
            self.assertEqual(result, 12)
            mock_sess.get.assert_called()

        with self.subTest("Expired token"):
            result = user.verify_token(self.expired_token)
            self.assertFalse(result)

        with self.subTest("Missing user"):
            mock_sess.get.return_value = None
            result = user.verify_token(self.good_token)
            self.assertTrue(result)

