"""
Schemas for request objects
"""

from marshmallow import Schema, fields, validates, validates_schema, ValidationError

from resource_allocator.db import get_session
from resource_allocator.models import (
    RequestModel, UserModel, IterationModel, ResourceModel, ResourceGroupModel,
)
from resource_allocator.schemas.base import BaseSchema


class RequestRequestSchema(Schema):
    iteration_id = fields.Integer(required=True)
    requested_date = fields.Date(required=True)
    user_id = fields.Integer(required=True)
    requested_resource_id = fields.Integer(allow_none=True)
    requested_resource_group_id = fields.Integer(allow_none=True)

    @validates("iteration_id")
    def validate_iteration_id(self, value):
        if not get_session().get(IterationModel, value):
            raise ValidationError(f"Iteration {value} does not exist")

    @validates("user_id")
    def validate_user_id(self, value):
        if not get_session().get(UserModel, value):
            raise ValidationError(f"User {value} does not exist")

    @validates("requested_resource_id")
    def validate_resource_id(self, value):
        if value and not get_session().get(ResourceModel, value):
            raise ValidationError(f"Resource {value} does not exist")

    @validates("requested_resource_group_id")
    def validate_resource_group_id(self, value):
        if value and not get_session().get(ResourceGroupModel, value):
            raise ValidationError(f"Resource {value} does not exist")

    @validates_schema
    def validate_request_or_group(self, data, **kwargs):
        if not (data["requested_resource_id"] or data["requested_resource_group_id"]):
            raise ValidationError(
                "Either resource or resource group must be requested"
            )


class RequestResponseSchema(BaseSchema, RequestRequestSchema):
    pass
