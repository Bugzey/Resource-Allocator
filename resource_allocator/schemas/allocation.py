"""
Allocation-related request schemas
"""

from marshmallow import Schema, fields, validates, validates_schema, ValidationError

from resource_allocator.db import get_session
from resource_allocator.schemas.base import BaseSchema
from resource_allocator.models import (
    IterationModel, UserModel, RequestModel, ResourceModel, AllocationModel,
)


class AllocationRequestSchema(Schema):
    iteration_id = fields.Integer(required=True)
    date = fields.Date(required=True)
    user_id = fields.Integer(required=True)
    source_request_id = fields.Integer(required=True)
    allocated_resource_id = fields.Integer(required=True)
    points = fields.Integer()

    @validates("iteration_id")
    def validate_iteration_id(self, value):
        iteration = get_session().get(IterationModel, value)
        if not iteration:
            raise ValidationError(f"Invalid iteration: {value}")

    @validates("user_id")
    def validate_user_id(self, value):
        if not get_session().get(UserModel, value):
            raise ValidationError(f"Invalid user: {value}")

    @validates("source_request_id")
    def validate_source_request_id(self, value):
        if not get_session().get(RequestModel, value):
            raise ValidationError(f"Invalid request: {value}")

    @validates("allocated_resource_id")
    def validate_allocated_resource_id(self, value):
        if not get_session().get(ResourceModel, value):
            raise ValidationError(f"Invalid resource: {value}")

    @validates_schema
    def validate_iteration_date(self, data, **kwargs):
        iteration = get_session().get(IterationModel, data["iteration_id"])
        date = data["date"]
        if not (date >= iteration.start_date and date <= iteration.end_date):
            raise ValidationError(
                f"Date {date} not within bounds: {iteration.start_date} - {iteration.end_date}"
            )

        #   Unique constraints - a resource OR user cannot be allocated again for a single day
        resource_allocated = (
            (AllocationModel.date == date) &
            (AllocationModel.allocated_resource_id == data["allocated_resource_id"])
        )
        user_allocated = (
            (AllocationModel.date == date) &
            (AllocationModel.user_id == data["user_id"])
        )
        if get_session().query(AllocationModel).where(resource_allocated | user_allocated).first():
            raise ValidationError(f"User or resource already allocated for date {data['date']}")


class AllocationAutomaticAllocationSchema(Schema):
    iteration_id = fields.Integer(required=True)

    @validates("iteration_id")
    def validate_iteration_id(self, value):
        iteration = get_session().get(IterationModel, value)
        if not iteration:
            raise ValidationError(f"Invalid iteration: {value}")

        if not iteration.accepts_requests:
            raise ValidationError(
                f"Iteration {value} does not accept requests or automatic allocation"
            )


class AllocationResponseSchema(BaseSchema, AllocationRequestSchema):
    pass

