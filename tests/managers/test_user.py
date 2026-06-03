"""
Tests for the managers.auth module
"""

import datetime as dt
import unittest
from unittest.mock import patch, MagicMock
from urllib.parse import quote

import jwt

from resource_allocator import models
from resource_allocator.models import (
    UserModel,
    RoleEnum,
)
from resource_allocator.config import Config
from resource_allocator.managers.user import (
    AuthManager,
    UserManager,
    verify_token,
)

from tests.managers.test_base import TestBase


@patch(
    "resource_allocator.managers.user.Config.get_instance",
    return_value=MagicMock(
        spec=Config,
        AZURE_CONFIGURED=True,
        LOCAL_LOGIN_ENABLED=True,
        SECRET="asdf1234" * 8,
        TENANT_ID="TENANT_ID",
        REDIRECT_URI="http://REDIRECT_URI",
        ALLOWED_ORIGINS=["http://localhost"],
    )
)
class AuthManagerTestCase(TestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
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
        self.manager = AuthManager(self.sess)

    def test_register_local(self, *args, **kwargs):
        result = self.manager.register(self.data)
        self.assertTrue(isinstance(result, dict))
        self.assertIn("token", result.keys())

        users = self.sess.query(models.UserModel).all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, self.data["email"])
        self.assertNotEqual(users[0].password_hash, self.data["password"])
        self.assertIsNotNone(users[0].role_id)

        #   First user is admin
        result = self.manager.register({**self.data, "email": "test2@example.com"})
        self._assert_first_user_is_admin()

    def _assert_first_user_is_admin(self, *args, **kwargs):
        roles = self.sess.query(models.RoleModel).all()
        admin_role = next((item.id for item in roles if item.role == "admin"))
        user_role = next((item.id for item in roles if item.role == "user"))
        users = self.sess.query(models.UserModel).all()
        self.assertEqual(users[0].role_id, admin_role)
        self.assertEqual(users[1].role_id, user_role)

    def test_login_ok(self, *args, **kwargs):
        _ = self.manager.register(self.data)
        result = self.manager.login(self.data)
        self.assertTrue(isinstance(result, dict))
        self.assertIn("token", result.keys())

    def test_login_invalid_password(self, *args, **kwargs):
        _ = self.manager.register(self.data)
        result = self.manager.login({**self.data, "password": "invalid_pass"})
        self.assertIn("Invalid password", result)

    def test_login_invalid_user(self, *args, **kwargs):
        _ = self.manager.register(self.data)
        result = self.manager.login({**self.data, "email": "bla@example.com"})
        self.assertIn("No such user", result[0])  # message

    def test_login_azure_init(self, *args, **kwargs):
        #   Default flow
        result = self.manager.login_azure_init()
        self.assertIsInstance(result, dict)
        self.assertIn("auth_url", result)
        self.assertIn("redirect_uri", result["auth_url"])
        self.assertIn("REDIRECT_URI", result["auth_url"])

        #   Valid custom redirect
        result = self.manager.login_azure_init({"redirect_uri": "http://localhost:9090/bla"})
        self.assertIsInstance(result, dict)
        self.assertIn("auth_url", result)
        self.assertIn(quote("http://localhost:9090/bla", safe=""), result["auth_url"])

        #   Invalid domains
        result = self.manager.login_azure_init({"redirect_uri": "https://hacker-domain.com"})
        self.assertIsInstance(result, tuple)
        self.assertIn("can only be localhost", result[0])
        self.assertIn("hacker-domain.com", result[0])

    def test_register_azure(self, *args, **kwargs):
        result = self.manager._register_azure(self.azure_response)
        self.assertTrue(isinstance(result, models.UserModel))

        users = self.sess.query(models.UserModel).all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, self.data["email"])
        self.assertIsNone(users[0].password_hash)
        self.assertIsNotNone(users[0].role_id)
        self.assertTrue(users[0].is_external)

        #   First user is admin
        result = self.manager.register({**self.data, "email": "test2@example.com"})
        self._assert_first_user_is_admin()

    @patch("resource_allocator.managers.user.get_azure_user_info")
    @patch("resource_allocator.managers.user.req.session")
    def test_login_azure_finish(
        self,
        req_session: MagicMock,
        get_azure_user_info: MagicMock,
        *args,
        **kwargs,
    ):
        auth_response = MagicMock()
        auth_response.send.return_value.ok = True
        auth_response.send.return_value.json.return_value = {"access_token": "access_token"}
        req_session.__enter__.return_value = auth_response
        get_azure_user_info.return_value = self.azure_response

        result = self.manager.login_azure_finish(
            data={
                "email": self.data["email"],
                "code": "some_code",
            },
        )
        self.assertTrue(isinstance(result, dict))
        self.assertIn("token", result.keys())

        users = self.sess.query(models.UserModel).all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, self.data["email"])
        self.assertIsNone(users[0].password_hash)
        self.assertIsNotNone(users[0].role_id)
        self.assertTrue(users[0].is_external)


@patch(
    "resource_allocator.managers.user.Config.get_instance",
    return_value=MagicMock(
        spec=Config,
        AZURE_CONFIGURED=True,
        LOCAL_LOGIN_ENABLED=True,
        SECRET="asdf1234" * 8,
        TENANT_ID="TENANT_ID",
        REDIRECT_URI="http://REDIRECT_URI",
        ALLOWED_ORIGINS=["http://localhost"],
    )
)
class UserManagerTestCase(TestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.users = [
            {
                "email": "admin@example.com",
                "password": 123456,
                "first_name": "bla",
                "last_name": "bla",
            },
            {
                "email": "user@example.com",
                "password": 123456,
                "first_name": "bla",
                "last_name": "bla",
            },
        ]
        self.auth_manager = AuthManager(self.sess)
        [self.auth_manager.register(user) for user in self.users]

    def test_get(self):
        result = UserManager.list_single_item(1)
        self.assertIsInstance(result, UserModel)
        self.assertEqual(result.email, self.users[0]["email"])
        self.assertEqual(result.role.role, RoleEnum.admin.value)

    def test_modify(self):
        #   Normal items
        old_user = UserManager.list_single_item(2)
        old_pass = old_user.password_hash
        result = UserManager.modify_item(
            2,
            {
                "first_name": "alb",
                "password": "123ABC",
            },
        )
        self.assertEqual(result.first_name, "alb")
        self.assertEqual(result.last_name, "bla")
        self.assertNotEqual(result.password_hash, old_pass)


@patch(
    "resource_allocator.managers.user.Config.get_instance",
    return_value=MagicMock(
        spec=Config,
        SECRET="asdf1234" * 8,
    )
)
class VerifyTokenTestCase(unittest.TestCase):
    def setUp(self):
        self.secret = "asdf1234" * 8
        now = dt.datetime.now(tz=dt.timezone.utc)
        self.data = {
            "sub": "12",
            "iat": now,
            "exp": now + dt.timedelta(seconds=3600),
        }
        self.good_token = jwt.encode(self.data, key=self.secret, algorithm="HS256")

        self.expired_token = jwt.encode(
            {
                **self.data,
                "exp": 0,
            },
            key=self.secret,
            algorithm="HS256",
        )

    @patch("resource_allocator.managers.user.get_session")
    def test_verify_token(self, mock_sess: MagicMock, *args, **kwargs):
        with self.subTest("Good token"):
            mock_sess.return_value.get.return_value = "12"
            result = verify_token(self.good_token)
            self.assertEqual(result, "12")
            mock_sess.return_value.get.assert_called()

        with self.subTest("Expired token"):
            result = verify_token(self.expired_token)
            self.assertFalse(result)

        with self.subTest("Missing user"):
            mock_sess.return_value.get.return_value = None
            result = verify_token(self.good_token)
            self.assertTrue(result)
