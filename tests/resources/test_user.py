"""
Unit tests for resources.user
"""

import unittest

from resource_allocator.resources import user

from tests.resources.test_base import ResourceTestBase


class UserAuthTestCase(ResourceTestBase, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.register(user.LoginUserAzureResource, "login_azure", rule="/login_azure/")

    def test_register(self):
        resp = self.register_user(email=f"user_{id(self)}_test_register@example.com")
        self.assertEqual(resp.status_code, 200)

    def test_register_duplicate(self):
        resp = self.register_user(email=f"dup_{id(self)}@example.com")
        self.assertEqual(resp.status_code, 200)

        resp = self.register_user(email=f"dup_{id(self)}@example.com")
        self.assertNotEqual(resp.status_code, 200)

    def test_login(self):
        _ = self.register_user()  # might fail but that's ok
        resp = self.login_user()

        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertIn("id", data)
        self.assertIn("token", data)


class UserTestCase(ResourceTestBase, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.register(user.UserResource, "users")

    def test_me(self):
        _ = self.register_user()
        resp = self.login_user()
        token = resp.json["token"]

        with self.client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        ) as resp:
            self.assertEqual(resp.status_code, 200)
            self.assertIn("id", resp.json)
            self.assertIn("email", resp.json)
            self.assertFalse(resp.json["is_external"])
