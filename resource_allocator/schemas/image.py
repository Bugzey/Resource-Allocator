"""
Schemas for imgae objects
"""

from marshmallow import fields

from resource_allocator.schemas.base import BaseSchema


class ImageRequestSchema(BaseSchema):
    image = fields.String(required=True)


class ImageResponseSchema(ImageRequestSchema):
    pass


class ImagePropertiesSchema(BaseSchema):
    box_x = fields.Integer()
    box_y = fields.Integer()
    box_width = fields.Integer()
    box_height = fields.Integer()
    box_rotation = fields.Float()
