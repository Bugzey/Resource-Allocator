"""
Schemas for imgae objects
"""

from marshmallow import fields

from resource_allocator.schemas.base import BaseRequestSchema, BaseResponseSchema


class ImageRequestSchema(BaseRequestSchema):
    image = fields.String(required=True)


class ImageResponseSchema(BaseResponseSchema, ImageRequestSchema):
    image_type_id = fields.Integer()
    size_bytes = fields.Integer()


class ImagePropertiesRequestSchema(BaseRequestSchema):
    box_x = fields.Float()
    box_y = fields.Float()
    box_width = fields.Float()
    box_height = fields.Float()
    box_rotation = fields.Float()


class ImagePropertiesResponseSchema(BaseResponseSchema, ImagePropertiesRequestSchema):
    pass
