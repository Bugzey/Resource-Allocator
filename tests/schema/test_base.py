import unittest

from resource_allocator.managers.base import FilterConfig, OrderByConfig
from resource_allocator.models import ResourceModel
from resource_allocator.schemas.base import QuerySchema


class QuerySchemaTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = QuerySchema(model=ResourceModel)

    def test_query_blank(self):
        result = self.schema.load({})
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("limit"), 200)
        self.assertEqual(result.get("page"), 1)
        self.assertIsInstance(result.get("filters"), FilterConfig)
        self.assertIsInstance(result.get("order_by"), OrderByConfig)

    def test_query_full(self):
        result = self.schema.load({
            "filter[name]": "bla",
            "filter[top_resource_group_id][isin]": "12,13",
            "order_by": ["name", "-top_resource_group_id"],
            "limit": 12,
            "page": 1,
        })
        self.assertIsInstance(result, dict)
        self.assertIn("filters", result)
        self.assertIsInstance(result["filters"], FilterConfig)
        self.assertEqual(result["filters"][0].field_name, "name")

        self.assertIn("order_by", result)
        self.assertIsInstance(result["order_by"], OrderByConfig)
        self.assertEqual(result["order_by"][1].field_name, "top_resource_group_id")
        self.assertEqual(result["order_by"][1].ascending, False)

    def test_invalid_model_fields(self):
        result = self.schema.validate({
            "filter[non_existent]": 12,
            "order_by": ["-non_existent"],
        })
        self.assertIsNotNone(result)
        self.assertIn("filters", result)
        self.assertIn("Filter columns do not exist", result["filters"][0])
        self.assertIn("non_existent", result["filters"][0])

        self.assertIn("order_by", result)
        self.assertIn("Order by columns do not exist", result["order_by"][0])
        self.assertIn("non_existent", result["order_by"][0])
