"""
Schemas for imgae objects
"""

from marshmallow import Schema, fields, validates, validates_schema, ValidationError

from resource_allocator.db import sess
from resource_allocator.models import ImageModel
from resource_allocator.schemas.base import BaseSchema

class ImageRequestSchema(Schema):
    image = fields.String(required = True)


class ImageResponseSchema(ImageRequestSchema):
    pass


class ImagePropertiesSchema(Schema):
    box_x = fields.Integer()
    box_y = fields.Integer()
    box_width = fields.Integer()
    box_height = fields.Integer()
    box_rotation = fields.Float()
