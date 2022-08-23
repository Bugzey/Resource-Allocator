"""
Tests for the managers.auth module
"""

import unittest
from unittest.mock import patch, MagicMock

from resource_allocator.db import engine, sess
from resource_allocator import models
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
