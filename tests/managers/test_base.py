"""
Tests for managers.base
"""

import unittest
from unittest.mock import patch, MagicMock

import sqlalchemy as db
from sqlalchemy import (Column, Integer, String)
from sqlalchemy.orm import declarative_base

from resource_allocator.db import sess, engine
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
        metadata.create_all(engine)
        self.item = {
            "name": "some_item",
        }

    def tearDown(self):
        sess.rollback()
        metadata.drop_all(engine)

    def test_create_item(self):
        item = self.SomeManager.create_item(self.item)
        self.assertTrue(isinstance(item, SomeTable))
        self.assertIsNotNone(item.id)

    def test_single_item(self):
        item = self.SomeManager.create_item(self.item)
        result = self.SomeManager.list_single_item(id = item.id)
        self.assertEqual(item, result)

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

