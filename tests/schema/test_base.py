import unittest

from resource_allocator.managers.base import FilterConfig, OrderByConfig
from resource_allocator.schemas.base import QuerySchema


class QuerySchemaTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = QuerySchema()

    def test_query_blank(self):
        result = self.schema.load({})
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("limit"), 200)
        self.assertEqual(result.get("page"), 1)
        self.assertIsInstance(result.get("filters"), FilterConfig)
        self.assertIsInstance(result.get("order_by"), OrderByConfig)

    def test_query_full(self):
        result = self.schema.load({
            "filter[some_field]": 12,
            "filter[other_field][isin]": "bla,alb",
            "order_by": ["some_field", "-other_field"],
            "limit": 12,
            "page": 1,
        })
        self.assertIsInstance(result, dict)
        self.assertIn("filters", result)
        self.assertIsInstance(result["filters"], FilterConfig)
        self.assertEqual(result["filters"][0].field_name, "some_field")

        self.assertIn("order_by", result)
        self.assertIsInstance(result["order_by"], OrderByConfig)
        self.assertEqual(result["order_by"][0].field_name, "some_field")
