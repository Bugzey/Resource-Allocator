"""
Iteration-related request schemas
"""

from marshmallow import (
    Schema,
    ValidationError,
    fields,
    validates_schema,
)

from resource_allocator.schemas.base import BaseSchema


class IterationRequestSchema(Schema):
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    accepts_requests = fields.Boolean()

    @validates_schema
    def validate_continuity(self, data, **kwargs):
        if data["start_date"] >= data["end_date"]:
            raise ValidationError("end_date must be later than start_date")


class IterationResponseSchema(BaseSchema, IterationRequestSchema):
    pass
