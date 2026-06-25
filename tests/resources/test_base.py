"""
Tests for base resources and related functions
"""

import datetime as dt
import unittest
from unittest.mock import patch, MagicMock

import jwt

from resource_allocator.config import Config
from resource_allocator.resources.base import (
    verify_token,
)


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
