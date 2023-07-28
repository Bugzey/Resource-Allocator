"""
Tests for managers.base
"""

import unittest

from sqlalchemy import String

from resource_allocator.config import Config
from resource_allocator.db import get_session
from resource_allocator.models import metadata, Base
from resource_allocator.utils.db import change_schema
from resource_allocator.managers.base import BaseManager


metadata = change_schema(metadata, "resource_allocator_test")


class SomeTable(Base):
    __tablename__ = "some_table"
    name = String(255)


class BaseManagerTestCase(unittest.TestCase):
    class SomeManager(BaseManager):
        model = SomeTable

    def setUp(self):
        self.config = Config.from_environment()
        self.sess = get_session()
        metadata.create_all(self.sess.bind)
        self.item = {
            "name": "some_item",
        }

    def tearDown(self):
        self.sess.rollback()
        metadata.drop_all(self.sess.bind)

    def test_create_item(self):
        item = self.SomeManager.create_item(self.item)
        self.assertTrue(isinstance(item, SomeTable))
        self.assertIsNotNone(item.id)

    def test_single_item(self):
        item = self.SomeManager.create_item(self.item)
        with self.subTest("Existing"):
            result = self.SomeManager.list_single_item(id=item.id)
            self.assertEqual(item, result)

        with self.subTest("Missing"):
            result = self.SomeManager.list_single_item(id=item.id - 1)
            self.assertIn("not found", result[0])

    def test_list_all_items(self):
        item = self.SomeManager.create_item(self.item)
        item = self.SomeManager.create_item(self.item)
        result = self.SomeManager.list_all_items()
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[-1], item)

    def test_delete_item(self):
        item = self.SomeManager.create_item(self.item)
        self.SomeManager.delete_item(item.id)
        result = self.SomeManager.list_all_items()
        self.assertEqual(len(result), 0)

        second_result = self.SomeManager.delete_item(item.id)
        self.assertIn("not found", second_result[0])
