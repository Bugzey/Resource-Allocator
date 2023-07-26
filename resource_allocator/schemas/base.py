"""
Base schema that includes regular fields
"""

from abc import ABC

from marshmallow import Schema, fields


class BaseSchema(Schema):
    id = fields.Integer(required=True)
    created_time = fields.DateTime(required=True)
    updated_time = fields.DateTime(required=True)
