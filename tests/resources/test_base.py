"""
Base test class for resource tests and tests for base resources and related functions
"""

import datetime as dt
import unittest
from unittest.mock import patch, MagicMock

import jwt
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from resource_allocator.config import Config
from resource_allocator.models import metadata, populate_enums
from resource_allocator.resources import user
from resource_allocator.resources.base import (
    verify_token,
)


TEST_SECRET = "asdf1234" * 8


class TestConfig(Config):
    """Real Config subclass that uses an in-memory SQLite engine."""

    def __init__(self, engine) -> None:
        self.AAD_CLIENT_ID = None
        self.AAD_CLIENT_SECRET = None
        self.TENANT_ID = None
        self.REDIRECT_URI = None
        self.LOCAL_LOGIN_ENABLED = True
        self.DB_DATABASE = "test"
        self.DB_HOST = "localhost"
        self.DB_PORT = 5432
        self.DB_USER = "test"
        self.DB_PASSWORD = "test"
        self.SECRET = TEST_SECRET
        self.SERVER_NAME = None
        self.ALLOWED_ORIGINS = []
        self._engine = engine
        self._sess = Session(engine)
        Config._instance.append(self)


class ResourceTestBase:
    """
    In-memory SQLite database + real TestConfig for resource endpoint tests.
    All paths (resources, managers, schemas, auth) work without external deps.
    """

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite+pysqlite:///:memory:")
        sess = Session(cls.engine)
        sess.execute(text('attach ":memory:" AS "resource_allocator"'))
        metadata.create_all(cls.engine)
        populate_enums(sess)
        sess.commit()

        Config.reset_instance()
        cls.config = TestConfig(cls.engine)

        cls.app = Flask(__name__)
        cls.client: FlaskClient = cls.app.test_client()

        #   Demo users
        cls.login_email = "user@example.com"
        cls.login_password = "123123ABCabc."
        cls.register(user.RegisterUserResource, "register", rule="/register/")
        cls.register(user.LoginUserResource, "login", rule="/login/")

    @classmethod
    def tearDownClass(cls):
        metadata.drop_all(cls.engine)
        cls.config._sess.close()
        cls.engine.dispose()
        Config.reset_instance()

    @classmethod
    def register(cls, resource_cls, name, rule=None):
        """Register a single resource on the test app."""
        if rule:
            resource_cls.register_view(cls.app, config=cls.config, name=name, rule=rule)
        else:
            resource_cls.register_view(cls.app, config=cls.config, name=name)

    @classmethod
    def register_user(self, email: str | None = None) -> TestResponse:
        with self.client.post(
            "/register/", json={
                "email": email or self.login_email,
                "password": self.login_password,
                "first_name": "first_name",
                "last_name": "last_name",
            }
        ) as resp:
            return resp

    @classmethod
    def login_user(self, email: str | None = None) -> TestResponse:
        with self.client.post(
            "/login/", json={
                "email": email or self.login_email,
                "password": self.login_password,
            },
        ) as resp:
            return resp


@patch(
    "resource_allocator.resources.base.Config.get_instance",
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

    @patch("resource_allocator.resources.base.get_session")
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
