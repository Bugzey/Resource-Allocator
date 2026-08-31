"""
Allocation-related request schemas
"""

from marshmallow import fields, pre_load, validates, validates_schema, ValidationError

from resource_allocator.db import get_session
from resource_allocator.schemas.base import BaseRequestSchema, BaseResponseSchema
from resource_allocator.models import (
    IterationModel, UserModel, RequestModel, ResourceModel, AllocationModel
)


class AllocationRequestSchema(BaseRequestSchema):
    iteration_id = fields.Integer(required=True)
    date = fields.Date(required=True)
    user_id = fields.Integer(required=True)
    user_for_id = fields.Integer(required=False)
    source_request_id = fields.Integer(required=True)
    allocated_resource_id = fields.Integer(required=True)
    points = fields.Integer()

    @pre_load
    def fill_in_user_for_id(self, data, **kwargs):
        if not data.get("user_for_id"):
            data["user_for_id"] = data.get("user_id")

        return data

    @validates("user_id", "iteration_id", "source_request_id", "allocated_resource_id")
    def validate_item_id(self, value, data_key):
        match data_key:
            case "user_id":
                model = UserModel
            case "source_request_id":
                model = RequestModel
            case "allocated_resource_id":
                model = ResourceModel
            case "iteration_id":
                model = IterationModel
            case _:
                raise ValueError(f"Invalid validation data key: {data_key}")

        if not get_session().get(model, value):
            raise ValidationError(f"Invalid value for {data_key}: {value}")

    @validates_schema
    def validate_iteration_bounds(self, data, **kwargs):
        iteration = get_session().get(IterationModel, data["iteration_id"])
        date = data["date"]
        if not (date >= iteration.start_date and date <= iteration.end_date):
            raise ValidationError(
                f"Date {date} not within bounds: {iteration.start_date} - {iteration.end_date}"
            )

    @validates_schema
    def validate_resource_already_allocated(self, data, **kwargs):
        """
        A resource is already allocated for the given date
        """
        date = data["date"]
        resource_id = data["allocated_resource_id"]
        sess = get_session()
        resource_allocated = (
            (AllocationModel.date == date)
            & (AllocationModel.allocated_resource_id == resource_id)
        )
        if sess.query(AllocationModel).where(resource_allocated).first():
            raise ValidationError(f"Resource {resource_id=} already allocated for {date}")


class AllocationAutomaticAllocationSchema(BaseRequestSchema):
    iteration_id = fields.Integer(required=True)
    request_id = fields.Integer()

    @validates("iteration_id")
    def validate_iteration_id(self, value, data_key):
        iteration = get_session().get(IterationModel, value)
        if not iteration:
            raise ValidationError(f"Invalid iteration: {value}")

    @validates("request_id")
    def validate_request_id(self, value, data_key):
        request = get_session().get(RequestModel, value)
        if not request:
            raise ValidationError(f"Invalid request_id. {value}")


class AllocationResponseSchema(BaseResponseSchema, AllocationRequestSchema):
    pass
