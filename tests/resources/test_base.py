"""
Unit tests for the base resource
"""

import unittest
from unittest.mock import patch, MagicMock

from flask import Flask
from marshmallow import Schema
from marshmallow.fields import Integer, String
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import BadRequest

from resource_allocator.resources.base import BaseResource


class RequestSchema(Schema):
    id = Integer()
    value = String()


class ResponseSchema(RequestSchema):
    pass


@patch("resource_allocator.resources.base.get_user_role", MagicMock(return_value="user"))
class BaseResourceTestCase(unittest.TestCase):
    class Resource(BaseResource):
        manager = None
        request_schema = RequestSchema
        response_schema = ResponseSchema
        read_roles_required = "user"
        write_roles_required = "user"

    @classmethod
    def setUpClass(cls):
        cls.app = Flask(__name__)
        cls.app.add_url_rule("/", endpoint="index", methods=["GET"], view_func=cls.Resource.get)

    def test_paginate(self):
        #   All blank
        result = self.Resource._paginate(MultiDict())
        self.assertEqual(result, (200, 0, []))

        #   All valid
        args = {
            "limit": "100",
            "offset": "12",
            "order_by": ["id", "-value"],
        }
        result = self.Resource._paginate(MultiDict(args))
        self.assertEqual(result, (100, 12, ["id", "-value"]))

        #   Invalid
        args = {
            "limit": "bla",
            "offset": "alb",
            "order_by": ["1", "alb"],
        }
        with self.assertRaises(BadRequest):
            _ = self.Resource._paginate(MultiDict(args))
