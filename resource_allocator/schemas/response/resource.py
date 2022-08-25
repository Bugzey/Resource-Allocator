"""
Resource-related response schemas
"""

from marshmallow import fields

from resource_allocator.schemas.base import BaseSchema

class ResourceResponseSchema(BaseSchema):
    name = fields.String(required = True)
    top_resource_group_id = fields.Integer(required = True)

class ResourceGroupResponseSchema(BaseSchema):
    name = fields.String(required = True)
    is_top_level = fields.Boolean(required = True)
    top_resource_group_id = fields.Integer(required = True)

