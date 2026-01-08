"""
Base schema that includes regular fields
"""

from marshmallow import Schema, fields, post_load


class BaseRequestSchema(Schema):
    id = fields.Integer()

    @post_load
    def drop_id(self, data: dict, **kwargs):
        """
        Drop an ID field in case it is given. This is needed for automatically populating a partial
        put request
        """
        data.pop("id", None)
        return data


class BaseResponseSchema(Schema):
    id = fields.Integer(required=True)
    created_time = fields.DateTime(required=True)
    updated_time = fields.DateTime(required=True)

    @post_load
    def drop_id(self, data: dict, **kwargs):
        """
        Cancel out BaseRequestSchema.drop_id in case a schema inherits from BaseRequestSchema
        """
        return data
