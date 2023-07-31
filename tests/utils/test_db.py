"""
Unit tests for the utils.db module
"""

import unittest

from resource_allocator.utils.db import change_schema, db


class ChangeSchemaTestCase(unittest.TestCase):
    def setUp(self):
        self.metadata = db.MetaData(schema="some_schema")
        self.table = db.Table(
            "some_table",
            self.metadata,
            db.Column("id", db.Integer, primary_key=True),
        )

    def test_change_schema(self):
        metadata = change_schema(metadata=self.metadata, schema="new_schema")
        self.assertTrue(isinstance(metadata, db.MetaData))
        self.assertEqual(metadata.schema, "new_schema")

        table_name, table = list(metadata.tables.items())[0]
        self.assertIn("new_schema", table_name)
        self.assertNotIn("some_schema", table_name)
        self.assertEqual(table.schema, "new_schema")
