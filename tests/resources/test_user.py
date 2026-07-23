"""
Unit tests for resources.user
"""

import unittest
from unittest.mock import MagicMock, patch

from flask import Flask

from resource_allocator.config import Config
from resource_allocator.resources import user

from tests.managers.test_base import TestBase


CONFIG = MagicMock(
    spec=Config,
    SECRET="asdf1234" * 8,
    TENANT_ID="TENANT_ID",
    REDIRECT_URI="REDIRECT_URI",
    ALLOWED_ORIGINS=["http://localhost"],
    _engine=None,
)


class RegisterUserTestCase(TestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        CONFIG.get_session.return_value = self.sess
        self.app = Flask(__name__)
        user.RegisterUserResource.register_view(
            self.app,
            config=CONFIG,
            name="register",
        )
        user.LoginUserResource.register_view(
            self.app,
            config=CONFIG,
            name="login",
        )
        user.LoginUserAzureResource.register_view(
            self.app,
            config=CONFIG,
            name="login_azure",
        )

        self.register_data = {
            "email": "test@example.com",
            "password": "123123ABCabc.",
            "first_name": "first_name",
            "last_name": "last_name",
        }
        self.login_data = {
            "email": "test@example.com",
            "password": "123123ABCabc.",
        }

    @patch("resource_allocator.schemas.user.get_session")
    def test_register_user(self, get_session):
        get_session.return_value = self.sess
        with self.app.test_client() as client:
            result = client.post("/register", json=self.register_data)
            self.assertEqual(result._status_code, 200)
            content = result.json

        self.assertIsNotNone(content)
        self.assertIn("id", content)
        self.assertIn("token", content)

    @patch("resource_allocator.schemas.user.get_session")
    def test_register_user_exists(self, get_session):
        get_session.return_value = self.sess
        with self.app.test_client() as client:
            result = client.post("/register", json=self.register_data)
            self.assertEqual(result._status_code, 200)

            result = client.post("/register", json=self.register_data)
            self.assertNotEqual(result._status_code, 200)
            content = b"".join(item for item in result.response)

        self.assertIsNotNone(content)
        self.assertIn(b"already registered", content)

    @patch("resource_allocator.schemas.user.get_session")
    def test_login(self, get_session):
        get_session.return_value = self.sess
        with self.app.test_client() as client:
            result = client.post("/register", json=self.register_data)
            self.assertEqual(result._status_code, 200)
            result = client.post("/login", json=self.login_data)
            self.assertEqual(result._status_code, 200)
            content = result.json

        self.assertIsNotNone(content)
        self.assertIn("id", content)
        self.assertIn("token", content)
