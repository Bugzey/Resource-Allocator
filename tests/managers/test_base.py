"""
Tests for managers.base
"""

import unittest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, Mapped

from resource_allocator.models import metadata, Base, populate_enums
from resource_allocator.managers.base import (
    BaseManager,
    Filter,
    FilterConfig,
    Operation,
    OrderBy,
    OrderByConfig,
)


class OperationTestCase(unittest.TestCase):
    def test_operation(self):
        self.assertEqual(Operation["eq"], Operation.eq)
        self.assertIn("eq", Operation)
        self.assertNotIn("non_existent", Operation)
        self.assertEqual(Operation.notin, "notin")


class FilterTestCase(unittest.TestCase):
    def test_defaults(self):
        result = Filter("field", 12)
        self.assertEqual(result.field_name, "field")
        self.assertEqual(result.value, 12)
        self.assertEqual(result.operation, Operation.eq)

    def test_explicit(self):
        result = Filter("some invalid field BLA", "string maybe?", "le")
        self.assertEqual(result.field_name, "some invalid field BLA")
        self.assertEqual(result.value, "string maybe?")
        self.assertIs(result.operation, Operation.le)

    def test_invalid_operation(self):
        with self.assertRaises(ValueError) as exc:
            _ = Filter("field_name", 12, "non-existent-operation")
            self.assertIn("Invalid operation", exc.msg)

    def test_from_key_basic_okay(self):
        result = Filter.from_key_value("filter[field]", 12)
        self.assertEqual(result.field_name, "field")
        self.assertEqual(result.value, 12)
        self.assertEqual(result.operation, Operation.eq)

    def test_from_key_operation_single_good(self):
        result = Filter.from_key_value("filter[field][isin]", 12)
        self.assertEqual(result.field_name, "field")
        self.assertEqual(result.value, ["12"])
        self.assertEqual(result.operation, Operation.isin)

    def test_from_key_operation_multiple_good(self):
        result = Filter.from_key_value("filter[field][notin]", "12,13,abvc")
        self.assertEqual(result.field_name, "field")
        self.assertEqual(result.value, ["12", "13", "abvc"])
        self.assertEqual(result.operation, Operation.notin)

    def test_from_key_bad_field(self):
        with self.assertRaises(ValueError) as exc:
            _ = Filter.from_key_value("filter[][", 12)
            self.assertIn("Invalid filter format", exc.msg)

    def test_from_key_bad_operation(self):
        with self.assertRaises(ValueError) as exc:
            _ = Filter.from_key_value("filter[][sdfasdf", 12)
            self.assertIn("Invalid filter format", exc.msg)


class FilterConfigTestCase(unittest.TestCase):
    def test_filter_config_ok(self):
        result = FilterConfig.from_request_dict({
            "filter[some_field]": "some_value",
            "filter[other_field][isin]": "12,13",
            "flatter": "not-a-filter",
        })
        self.assertEqual(len(result), 2)

    def test_filter_config_bad(self):
        with self.assertRaises(ValueError) as exc:
            _ = FilterConfig.from_request_dict({
                "filter[]": 12,
                "filter[field][non-existent]": "non-existent",
                "filter[field][malformed.jasldfjksldfj": "malformed",
                "flatter": "not-a-filter",
            })
            self.assertIn("Error parsing filters: 3", exc.msg)


class OrderByTestCase(unittest.TestCase):
    def test_init(self):
        result = OrderBy("some_field")
        self.assertEqual(result.field_name, "some_field")
        self.assertTrue(result.ascending)

        result = OrderBy("-other_field")
        self.assertEqual(result.field_name, "other_field")
        self.assertFalse(result.ascending)


class OrderByConfigTestCase(unittest.TestCase):
    def test_from_key_value(self):
        result = OrderByConfig.from_key_value({"order_by": ["some_field", "-other_field"]})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].field_name, "some_field")
        self.assertTrue(result[0].ascending)
        self.assertEqual(result[1].field_name, "other_field")
        self.assertFalse(result[1].ascending)


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
        self.item = {"name": "some_item"}
        self.item_2 = {"name": "other_item"}
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

    def test_list_all_items_pagination(self):
        _ = self.manager.create_item(self.item)
        _ = self.manager.create_item(self.item_2)
        result = self.manager.list_all_items(limit=1, page=1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 1)

        result = self.manager.list_all_items(limit=1, page=2)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 2)

        result = self.manager.list_all_items(limit=1, page=99)
        self.assertEqual(len(result), 0)

    def test_list_all_items_filter(self):
        _ = self.manager.create_item(self.item)
        _ = self.manager.create_item(self.item_2)

        with self.subTest("No filter"):
            result = self.manager.list_all_items()
            self.assertEqual(len(result), 2)
            self.assertNotEqual(result[0].id, result[1].id)

        with self.subTest("Single eq filter"):
            result = self.manager.list_all_items(
                filters=FilterConfig([Filter("name", "some_item")])
            )
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, "some_item")

        with self.subTest("GT filter"):
            result = self.manager.list_all_items(
                filters=FilterConfig([Filter("id", 1, "gt")])
            )
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].id, 2)

        with self.subTest("GE filter"):
            result = self.manager.list_all_items(
                filters=FilterConfig([Filter("id", 1, "ge")])
            )
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0].id, 1)
            self.assertEqual(result[1].id, 2)

        with self.subTest("ISIN filter"):
            result = self.manager.list_all_items(
                filters=FilterConfig([Filter("name", "some_item,fake_item", "isin")])
            )
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, "some_item")

        with self.subTest("NOTIN filter"):
            result = self.manager.list_all_items(
                filters=FilterConfig([Filter("name", ["other_item", "fake_item"], "notin")])
            )
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, "some_item")

    def test_list_all_items_order_by(self):
        _ = self.manager.create_item(self.item)
        _ = self.manager.create_item(self.item_2)

        result = self.manager.list_all_items(
            order_by=OrderByConfig([OrderBy("id", ascending=False), OrderBy("name")]),
        )
        self.assertEqual(len(result), 2)
        self.assertGreater(result[0].id, result[1].id)

    def test_delete_item(self):
        item = self.manager.create_item(self.item)
        self.manager.delete_item(item.id)
        result = self.manager.list_all_items()
        self.assertEqual(result, [])

        second_result = self.manager.delete_item(item.id)
        self.assertIsNone(second_result)
