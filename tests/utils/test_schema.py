"""
Unittests for utils.schema
"""

import datetime as dt
import unittest
from unittest.mock import patch, MagicMock

from marshmallow import Schema, fields

from resource_allocator.main import create_app
from resource_allocator.utils.schema import *


class ValidateSchemaTestCase(unittest.TestCase):
    class SomeSchema(Schema):
        id = fields.Int(required=True)
        name = fields.String(required=True)

    def setUp(self):
        self.good_data = {
            "id": 12,
            "name": "bla",
        }
        self.bad_fields = {
            "id": "bla",
            "name": 12,
        }
        self.missing_fields = {
            "bla": 12,
        }
        self.some_fun = validate_schema(self.SomeSchema)(lambda: request.json)
        self.app = create_app()
        self.app.add_url_rule("/test", view_func=self.some_fun)

    def test_validate_schema(self):
        with self.subTest("Good fields"):
            with self.app.test_request_context(
                "/test", method="POST", json=self.good_data,
            ):
                result = self.some_fun()
                self.assertEqual(result, self.good_data)

        with self.subTest("Bad fields"):
            with self.app.test_request_context(
                "/test", method="POST", json=self.bad_fields,
            ):
                result = self.some_fun()
                self.assertIn(400, result)
                self.assertIn("Data validation errors", result[0])
                self.assertIn("id", result[0])
                self.assertIn("name", result[0])

        with self.subTest("Missing fields"):
            with self.app.test_request_context(
                "/test", method="POST", json=self.missing_fields,
            ):
                result = self.some_fun()
                self.assertIn(400, result)
                self.assertIn("Unknown", result[0])
                self.assertIn("Missing", result[0])
