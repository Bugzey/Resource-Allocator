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


class ImageMixInSchema(Schema):
    image = fields.Nested(ImageRequestSchema)
    box_y = fields.Integer()
    box_x = fields.Integer()
    box_width = fields.Integer()
    box_height = fields.Integer()
    box_rotation = fields.Float()

    @validates_schema
    def validate_image_is_given(self, data, **kwargs):
        if (
            (not data["image"]) and (data["box_x"] or data["box_y"] or data["box_width"] \
            or data["box_height"] or data["box_rotation"])
        ):
            raise ValidationError(
                "Image must be given if any of box_x, box_y, box_width, box_height or box_rotation "
                "are given"
            )

