"""
Resource... resource test case - proxy for all BaseResource-derived objects
"""

import unittest

from resource_allocator.main import create_app
from resource_allocator.config import Config
from resource_allocator.db import get_session
from resource_allocator.models import metadata, populate_enums
from resource_allocator.resources import ResourceResource
from resource_allocator.utils.db import change_schema
from resource_allocator.managers import (
    ResourceManager,
    ResourceGroupManager,
    AuthManager,
)


metadata = change_schema(metadata, schema="resource_allocator_test")


class ResourceResourceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Config.from_environment()
        self.sess = get_session()
        self.engine = self.sess.bind
        self.app = create_app()
        metadata.drop_all(self.engine)  # in case of errors during setUp
        metadata.create_all(self.engine)
        populate_enums(self.sess)

        #   Data
        self.user = AuthManager.register({
            "email": "test@example.com",
            "password": "password",
            "first_name": "first_name",
            "last_name": "last_name",
        })
        self.headers = {"Authorization": f"Bearer {self.user['token']}"}

        self.group = ResourceGroupManager.create_item({
            "name": "top_level",
            "is_top_level": True,
        })
        self.resource = ResourceManager.create_item({
            "name": "resource",
            "top_resource_group_id": self.group.id,
        })

    @classmethod
    def tearDownClass(self):
        self.sess.flush()
        self.sess.rollback()
        metadata.drop_all(bind=self.engine)

    def test_get(self):
        with self.app.test_request_context(headers=self.headers):
            result = ResourceResource().get(self.resource.id)
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertEqual(result["name"], "resource")

    def test_post(self):
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

    def test_delete(self):
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

    def test_put(self):
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
