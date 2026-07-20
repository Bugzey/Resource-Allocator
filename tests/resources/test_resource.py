"""
Resource... resource test case - proxy for all BaseResource-derived objects
"""

import unittest
from unittest.mock import MagicMock, patch

from flask import Flask

from resource_allocator.config import Config
from resource_allocator.resources import ResourceResource
from resource_allocator.resources import user
from resource_allocator.managers import (
    ResourceManager,
    ResourceGroupManager,
)

from tests.managers.test_base import TestBase


#   Config
CONFIG = MagicMock(
    spec=Config,
    SECRET="asdf1234" * 8,
    TENANT_ID="TENANT_ID",
    REDIRECT_URI="REDIRECT_URI",
    ALLOWED_ORIGINS=["http://localhost"],
    _engine=None,
)


@unittest.skip("Ugh")
@patch("resource_allocator.config.Config.get_instance", return_value=CONFIG)
class ResourceResourceTestCase(TestBase, unittest.TestCase):
    @classmethod
    def setUpClass(self):
        #   System
        super().setUp(self)
        CONFIG._engine = self.engine
        self.app = Flask(__name__)
        user.RegisterUserResource.register_method_view(
            self.app,
            "register",
            sess=self.sess,
            config=CONFIG,
        )
        user.LoginUserResource.register_method_view(
            self.app,
            "login",
            sess=self.sess,
            config=CONFIG,
        )
        ResourceResource.register_method_view(self.app, "resources", sess=self.sess, config=CONFIG)

        #   Data
        with self.app.test_client() as client:
            result = client.post("/register", json={
                "email": "test@example.com",
                "password": "password",
                "first_name": "first_name",
                "last_name": "last_name",
            })
            self.headers = {"Authorization": f"Bearer {result.json['token']}"}

        self.group = ResourceGroupManager(self.sess).create_item({
            "name": "top_level",
            "is_top_level": True,
        })
        self.resource = ResourceManager(self.sess).create_item({
            "name": "resource",
            "top_resource_group_id": self.group.id,
        })

    @classmethod
    def tearDownClass(self):
        super().tearDown(self)

    def test_get(self, *args, **kwargs):
        result = self.client.get(path=f"/resources/{self.resource.id}")
        breakpoint()
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertEqual(result["name"], "resource")

    def test_post(self, *args, **kwargs):
        with self.app.test_request_context(
            headers=self.headers,
            json={
                "name": "new",
                "top_resource_group_id": self.group.id,
            },
        ):
            result = ResourceResource().post()
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertEqual(result["name"], "new")

    def test_delete(self, *args, **kwargs):
        with self.app.test_request_context(
            headers=self.headers,
            json={
                "name": "deleted",
                "top_resource_group_id": self.group.id,
            },
        ):
            result = ResourceResource().post()
            result = ResourceResource().delete(result["id"])
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertEqual(result["name"], "deleted")
        self.assertIsNone(ResourceManager.list_single_item(result["id"]))

    def test_put(self, *args, **kwargs):
        with self.app.test_request_context(
            headers=self.headers,
            json={
                "name": "to_change",
                "top_resource_group_id": self.group.id,
            },
        ):
            result = ResourceResource().post()

        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertEqual(result["name"], "to_change")

        with self.app.test_request_context(
            headers=self.headers,
            json={
                "name": "changed",
            },
        ):
            result = ResourceResource().put(result["id"])

        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertEqual(result["name"], "changed")
        self.assertEqual(result["top_resource_group_id"], self.group.id)
