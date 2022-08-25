"""
Request-related schemas for resource objects
"""

from marshmallow import Schema, fields, validates, ValidationError

from resource_allocator.db import sess
from resource_allocator.models import ResourceModel, ResourceGroupModel

class ResourceRequestSchema(Schema):
    name = fields.String(required = True)
    top_resource_group_id = fields.Integer(required = True)

    @validates("name")
    def validate_name(self, value):
        if sess.query(ResourceModel.id).where(ResourceModel.name == value).scalar():
            raise ValidationError(f"Name: {value} already exists")

    @validates("top_resource_group_id")
    def validate_top_resource_group_id(self, value):
        if not sess.get(ResourceGroupModel, value):
            raise ValidationError(f"Invalid top_resource_group_id: {value}")


class ResourceGroupRequestSchema(Schema):
    name = fields.String(required = True)
    top_resource_group_id = fields.Integer(required = True)
    is_top_level = fields.Boolean(required = True)
    top_resource_group_id = fields.Integer()

    @validates("name")
    def validate_name(self, value):
        if sess.query(ResourceGroupModel.id).where(ResourceGroupModel.name == value).scalar():
            raise ValidationError(f"Name: {value} already exists")

    @validates("top_resource_group_id")
    def validate_top_resource_group_id(self, value):
        if not sess.get(ResourceGroupModel, value):
            raise ValidationError(f"Invalid top_resource_group_id: {value}")

