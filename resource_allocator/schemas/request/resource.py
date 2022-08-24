"""
Request-related schemas for resource objects
"""

from marshmallow import Schema, fields, validates, ValidationError

from resource_allocator.db import sess
from resource_allocator.models import ResourceModel

class ResourceRequestSchema(Schema):
    name = fields.String(required = True)

    @validates("name")
    def validate_name(self, value):
        if sess.query(ResourceModel.id).where(ResourceModel.name == value).scalar():
            raise ValidationError(f"Name: {value} already exists")


class ResourceGroupRequestSchema(Schema):
    name = fields.String(required = True)

    @validates("name")
    def validate_name(self, value):
        if sess.query(ResourceGroupModel.id).where(ResourceGroupModel.name == value).scalar():
            raise ValidationError(f"Name: {value} already exists")

