"""
Request-related schemas for resource objects
"""

from marshmallow import Schema, fields, validates, ValidationError

from resource_allocator.db import get_session
from resource_allocator.models import (
    ImageModel,
    ImagePropertiesModel,
    ResourceGroupModel,
    ResourceModel,
)
from resource_allocator.schemas.base import BaseSchema


class ResourceRequestSchema(Schema):
    name = fields.String(required=True)
    top_resource_group_id = fields.Integer(required=True)
    image_id = fields.Integer()
    image_properties_id = fields.Integer()

    @validates("name")
    def validate_name(self, value):
        if get_session().query(ResourceModel.id).where(ResourceModel.name == value).scalar():
            raise ValidationError(f"Name: {value} already exists")

    @validates("top_resource_group_id")
    def validate_top_resource_group_id(self, value):
        if not get_session().get(ResourceGroupModel, value):
            raise ValidationError(f"Invalid top_resource_group_id: {value}")

    @validates("image_id")
    def validate_image_id(self, value):
        sess = get_session()
        if not sess.get(ImageModel, value):
            raise ValidationError(f"Invalid image_id: {value}")

    @validates("image_properties_id")
    def validate_image_properties_id(self, value):
        sess = get_session()
        if not sess.get(ImagePropertiesModel, value):
            raise ValidationError(f"Invalid image_properties_id: {value}")


class ResourceResponseSchema(BaseSchema):
    name = fields.String(required=True)
    top_resource_group_id = fields.Integer(required=True)
    image_id = fields.Integer()
    image_properties_id = fields.Integer()
