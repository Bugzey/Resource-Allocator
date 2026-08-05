"""
Base schema that includes regular fields
"""

from marshmallow import (
    EXCLUDE,
    Schema,
    fields,
    post_load,
    pre_load,
    validate,
    validates,
    ValidationError,
)
from marshmallow.fields import (
    DateTime,
    Integer,
    Raw,
)

from resource_allocator.managers.base import FilterConfig, OrderByConfig
from resource_allocator.models import Base


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
    model: Base

    def __init__(self, *args, model: Base, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

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
        try:
            filters = FilterConfig.from_request_dict(data)
        except ValueError as e:
            raise ValidationError(e.args[0], field_name="filters")
        data["filters"] = filters
        return data

    @pre_load
    def get_order_by(self, data: dict, *args, **kwargs):
        """
        Parse order by that should be a list of items
        """
        try:
            order_by = OrderByConfig.from_request_dict(data)
        except ValueError as e:
            raise ValidationError(e.args[0], field_name="order_by")

        data["order_by"] = order_by
        return data

    @validates("filters")
    def filter_cols_exist(self, filters: FilterConfig, *args, **kwargs):
        cols = self.model.__table__.columns
        invalid_cols = [item.field_name for item in filters if item.field_name not in cols]
        if invalid_cols:
            raise ValidationError(
                f"Filter columns do not exist in model: "
                f"{', '.join(invalid_cols)}"
            )

    @validates("order_by")
    def order_by_cols_exist(self, order_by: OrderByConfig, *args, **kwargs):
        cols = self.model.__table__.columns
        invalid_cols = [item.field_name for item in order_by if item.field_name not in cols]
        if invalid_cols:
            raise ValidationError(
                f"Order by columns do not exist in model: "
                f"{', '.join(invalid_cols)}"
            )
