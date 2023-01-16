"""
Request-related schemas for resource objects
"""

from marshmallow import Schema, fields, validates, validates_schema, ValidationError

from resource_allocator.db import get_session
from resource_allocator.models import ResourceModel, ResourceGroupModel
from resource_allocator.schemas.base import BaseSchema
from resource_allocator.schemas.image import ImageMixInSchema


class ResourceRequestSchema(ImageMixInSchema, Schema):
    name = fields.String(required = True)
    top_resource_group_id = fields.Integer(required = True)

    @validates("name")
    def validate_name(self, value):
        if get_session().query(ResourceModel.id).where(ResourceModel.name == value).scalar():
            raise ValidationError(f"Name: {value} already exists")

    @validates("top_resource_group_id")
    def validate_top_resource_group_id(self, value):
        if not get_session().get(ResourceGroupModel, value):
            raise ValidationError(f"Invalid top_resource_group_id: {value}")


class ResourceResponseSchema(ImageMixInSchema, BaseSchema):
    name = fields.String(required = True)
    top_resource_group_id = fields.Integer(required = True)

