"""
Schemas for request objects
"""

from marshmallow import (
    Schema,
    fields,
    validates,
    validates_schema,
    ValidationError,
)
from sqlalchemy import select, or_

from resource_allocator.db import get_session
from resource_allocator.models import (
    UserModel,
    IterationModel,
    RequestModel,
    ResourceModel,
    ResourceGroupModel,
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
        resource = data.get("requested_resource_id")
        group = data.get("requested_resource_group_id")
        if (resource is None and group is None) or (resource is not None and group is not None):
            raise ValidationError(
                "Either resource or resource group must be requested"
            )

    @validates_schema
    def validate_one_user_per_date(self, data, **kwargs):
        resource = data.get("requested_resource_id")
        group = data.get("requested_resource_group_id")

        sess = get_session()
        if resource:
            top_group = sess.get(ResourceModel, resource).top_resource_group
        elif group:
            top_group = sess.get(ResourceGroupModel, group).top_resource_group
        else:
            raise ValidationError("Neither resource nor group requested")

        query = (
            select(RequestModel)
            .outerjoin(ResourceGroupModel)
            .outerjoin(
                ResourceModel,
                RequestModel.requested_resource_id == ResourceModel.id
            )
            .where(
                RequestModel.iteration_id == data.get("iteration_id"),
                RequestModel.user_id == data.get("user_id"),
                RequestModel.requested_date == data.get("requested_date"),
                or_(
                    ResourceModel.top_resource_group_id == top_group.id,
                    ResourceGroupModel.top_resource_group_id == top_group.id,
                )
            )
        )
        if sess.scalars(query).first():
            raise ValidationError(
                "User already has a request for the given top resource group, date and iteration"
            )


class RequestResponseSchema(BaseSchema, RequestRequestSchema):
    pass
