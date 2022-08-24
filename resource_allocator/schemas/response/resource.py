"""
Resource-related response schemas
"""

from marshmallow import fields

from resource_allocator.schemas.base import BaseSchema

class ResourceResponseSchema(BaseSchema):
    name = fields.String(required = True)

