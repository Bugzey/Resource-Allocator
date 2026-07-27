"""
Tests for managers.base
"""

import unittest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, Mapped

from resource_allocator.models import metadata, Base, populate_enums
from resource_allocator.managers.base import BaseManager


class SomeTable(Base):
    __tablename__ = "some_table"
    name: Mapped[str]


class TestBase:
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        self.sess = Session(self.engine)
        self.sess.execute(text("attach \":memory:\" as \"resource_allocator\""))
        metadata.create_all(self.engine)
        populate_enums(self.sess)

    def tearDown(self):
        self.sess.rollback()
        metadata.drop_all(self.sess.bind)
        self.sess.close()
        self.engine.dispose()


class BaseManagerTestCase(TestBase, unittest.TestCase):
    class SomeManager(BaseManager):
        model = SomeTable

    def setUp(self):
        super().setUp()
        self.item = {
            "name": "some_item",
        }
        self.manager = self.SomeManager(self.sess)

    def test_create_item(self):
        item = self.manager.create_item(self.item)
        self.assertTrue(isinstance(item, SomeTable))
        self.assertIsNotNone(item.id)

    def test_single_item(self):
        item = self.manager.create_item(self.item)
        with self.subTest("Existing"):
            result = self.manager.list_single_item(id=item.id)
            self.assertEqual(item, result)

        with self.subTest("Missing"):
            result = self.manager.list_single_item(id=item.id - 1)
            self.assertIsNone(result)

    def test_list_all_items(self):
        item = self.manager.create_item(self.item)
        item = self.manager.create_item(self.item)
        result = self.manager.list_all_items()
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[-1], item)

    def test_delete_item(self):
        item = self.manager.create_item(self.item)
        self.manager.delete_item(item.id)
        result = self.manager.list_all_items()
        self.assertEqual(result, [])

        second_result = self.manager.delete_item(item.id)
        self.assertIsNone(second_result)
