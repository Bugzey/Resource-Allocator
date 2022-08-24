"""
Request-related schemas for resource objects
"""

from marshmallow import Schema, fields, validates

from resource_allocator.db import sess, ResourceModel, ValidationError

class ResourceRequestSchema(Schema):
    name = fields.String(required = True)

    @validates("name")
    def validate_name(self, value):
        if sess.query(ResourceModel.id).where(ResourceModel.name == value).scalar():
            raise ValidationError(f"{name} already exists")

