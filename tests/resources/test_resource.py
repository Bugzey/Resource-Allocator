"""
Resource CRUD endpoint tests - proxy for all CRUD-derived objects
"""

import unittest

from resource_allocator.managers import (
    ResourceManager,
    ResourceGroupManager,
)
from resource_allocator.resources.resource import ResourceResource

from tests.resources.test_base import ResourceTestBase


class ResourceCRUDTestCase(ResourceTestBase, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.register(ResourceResource, "resources")

        #   User
        resp = cls.register_user()
        cls.auth = {
            "Authorization": f"Bearer {resp.json['token']}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        cls.group = ResourceGroupManager(cls.config._sess).create_item({
            "name": "top_level",
            "is_top_level": True,
        })
        cls.resource_1 = ResourceManager(cls.config._sess).create_item({
            "name": "resource",
            "top_resource_group_id": cls.group.id,
        })
        cls.resource_2 = ResourceManager(cls.config._sess).create_item({
            "name": "other",
            "top_resource_group_id": cls.group.id,
        })

    def test_get_list_no_args(self):
        with self.client.get("/resources/", headers=self.auth) as resp:
            self.assertEqual(resp.status_code, 200)
            data = resp.json
        self.assertIsInstance(data, list)
        ids = [item["id"] for item in data]
        self.assertIn(self.resource_1.id, ids)

    def test_get_list_filter(self):
        with self.client.get(
            "/resources/",
            headers=self.auth,
            query_string={
                "filter[name]": "resource",
            },
        ) as resp:
            self.assertEqual(resp.status_code, 200)
            data = resp.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "resource")

    def test_get_list_multiple_order_by(self):
        with self.client.get(
            "/resources/",
            headers=self.auth,
            query_string={
                "order_by": ["-id", "name"],
                "limit": 1,
            },
        ) as resp:
            self.assertEqual(resp.status_code, 200)
            data = resp.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], 2)
        self.assertEqual(data[0]["name"], "other")

    def test_get_list_pagination(self):
        with self.client.get(
            "/resources/",
            headers=self.auth,
            query_string={
                "limit": 1,
                "page": 2,
                "order_by": ["id"],
            },
        ) as resp:
            self.assertEqual(resp.status_code, 200)
            data = resp.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], 2)
        self.assertEqual(data[0]["name"], "other")

    def test_get_list_invalid_filters_order_by(self):
        with self.client.get(
            "/resources/",
            headers=self.auth,
            query_string={
                "filter[invalid_col]": 12,
                "order_by": ["-invalid_col"],
            },
        ) as resp:
            self.assertEqual(resp.status_code, 400)

    def test_get_single(self):
        with self.client.get(f"/resources/{self.resource_1.id}", headers=self.auth) as resp:
            self.assertEqual(resp.status_code, 200)
            data = resp.json
        self.assertIsInstance(data, dict)
        self.assertIn("name", data)
        self.assertEqual(data["name"], "resource")

    def test_post(self):
        with self.client.post("/resources/", headers=self.auth, json={
            "name": "new",
            "top_resource_group_id": self.group.id,
        }) as resp:
            self.assertEqual(resp.status_code, 200)
            data = resp.json
        self.assertIsInstance(data, dict)
        self.assertEqual(data["name"], "new")

    def test_put(self):
        with self.client.post("/resources/", headers=self.auth, json={
            "name": "to_change",
            "top_resource_group_id": self.group.id,
        }) as resp:
            resource_id = resp.json["id"]

        with self.client.put(f"/resources/{resource_id}", headers=self.auth, json={
            "name": "changed",
        }) as resp:
            self.assertEqual(resp.status_code, 200)
            data = resp.json

        self.assertEqual(data["name"], "changed")
        self.assertEqual(data["top_resource_group_id"], self.group.id)

    def test_delete(self):
        with self.client.post("/resources/", headers=self.auth, json={
            "name": "to_delete",
            "top_resource_group_id": self.group.id,
        }) as resp:
            resource_id = resp.json["id"]

        with self.client.delete(f"/resources/{resource_id}", headers=self.auth) as resp:
            self.assertEqual(resp.status_code, 200)
            data = resp.json

        self.assertEqual(data["name"], "to_delete")
        self.assertIsNone(
            ResourceManager(self.config._sess).list_single_item(resource_id)
        )
