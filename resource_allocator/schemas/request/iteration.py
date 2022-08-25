"""
Iteration-related request schemas
"""

from marshmallow import fields, validates, validates_schema, ValidationError

from resource_allocator.schemas.base import BaseSchema

class IterationRequestSchema(BaseSchema):
    start_time = fields.DateTime(required = True)
    end_time = fields.DateTime(required = True)

    @validates_schema
    def validate_continuity(self, data, **kwargs):
        if data["start_time"] >= data["end_time"]:
            raise ValidationError("end_date must be later than start_date")

