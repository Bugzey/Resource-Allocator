"""
Schemas for imgae objects
"""

from marshmallow import fields, Schema

from resource_allocator.schemas.base import BaseSchema


class ImageRequestSchema(Schema):
    image = fields.String(required=True)


class ImageResponseSchema(BaseSchema, ImageRequestSchema):
    image_type_id = fields.Integer()
    size_bytes = fields.Integer()


class ImagePropertiesRequestSchema(Schema):
    box_x = fields.Float()
    box_y = fields.Float()
    box_width = fields.Float()
    box_height = fields.Float()
    box_rotation = fields.Float()


class ImagePropertiesResponseSchema(BaseSchema, ImagePropertiesRequestSchema):
    pass
