"""
Resource to Group schemas
"""

from marshmallow import Schema, fields, validates, ValidationError

from resource_allocator.db import get_session
from resource_allocator.models import ResourceModel, ResourceGroupModel
from resource_allocator.schemas.base import BaseSchema


class ResourceToGroupRequestSchema(Schema):
    resource_id = fields.Integer(required = True)
    resource_group_id = fields.Integer(required = True)

    @validates("resource_id")
    def validate_resource_id(self, value):
        if not get_session().get(ResourceModel, value):
            raise ValidationError(f"Invalid resource_id: {value}")

    @validates("resource_group_id")
    def validate_resource_group_id(self, value):
        if not get_session().get(ResourceGroupModel, value):
            raise ValidationError(f"Invalid resource_group_id: {value}")


class ResourceToGroupResponseSchema(BaseSchema, ResourceToGroupRequestSchema):
    pass

