"""
Base schema that includes regular fields
"""

from marshmallow import Schema, EXCLUDE, fields, post_load, pre_load, validate
from marshmallow.fields import (
    DateTime,
    Integer,
    Raw,
)

from resource_allocator.managers.base import FilterConfig, OrderByConfig


class BaseRequestSchema(Schema):
    id = Integer()

    @post_load
    def drop_id(self, data: dict, **kwargs):
        """
        Drop an ID field in case it is given. This is needed for automatically populating a partial
        put request
        """
        data.pop("id", None)
        return data


class BaseResponseSchema(Schema):
    id = Integer(required=True)
    created_time = DateTime(required=True)
    updated_time = DateTime(required=True)

    @post_load
    def drop_id(self, data: dict, **kwargs):
        """
        Cancel out BaseRequestSchema.drop_id in case a schema inherits from BaseRequestSchema
        """
        return data


class QuerySchema(Schema):
    """
    Schema to validate a query string for the shared get endpoint
    """
    class Meta(Schema.Meta):
        unknown = EXCLUDE

    filters = Raw()
    order_by = Raw()
    limit = fields.Integer(validate=validate.Range(1, 200), load_default=200)
    page = fields.Integer(validate=validate.Range(1), load_default=1)

    @pre_load
    def get_filters(self, data: dict, *args, **kwargs):
        """
        Parse a query string of the form filter[field]=12&filter[field][operation]=a,b
        """
        filters = FilterConfig.from_request_dict(data)
        data["filters"] = filters
        return data

    @pre_load
    def get_order_by(self, data: dict, *args, **kwargs):
        """
        Parse order by
        """
        order_by = OrderByConfig.from_request_dict(data)
        data["order_by"] = order_by
        return data
