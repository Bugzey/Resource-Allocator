"""
Image manager
"""

from io import BytesIO
from typing import Optional

import sqlalchemy as db
from PIL import Image

from resource_allocator.db import sess
from resource_allocator.models import (
    ImageModel, ImageTypeModel,
)
from resource_allocator.managers.base import BaseManager


class ImageTypeManager(BaseManager):
    model = ImageTypeModel


class ImageManager(BaseManager):
    model = ImageModel

    @classmethod
    def _parse_image(cls, data: dict) -> dict:
        with Image.open(BytesIO(data["image"])) as image:
            image_type = image.format
            image_type_id = sess \
                .query(ImageTypeModel.id) \
                .where(ImageTypeModel.image_type == image_type) \
                .scalar()

            if not image_type_id:
                new_image_type = ImageTypeModel(image_type = image_type)
                sess.add(new_image_type)
                sess.flush()
                image_type_id = new_image_type.id

        return {
            "image_data": data["image"],
            "image_type_id": image_type_id,
            "size_bytes": len(data["image"]),
        }

    @classmethod
    def create_item(cls, data: dict) -> db.Table:
        data = cls._parse_image(data)
        return super().create_item(data)

    @classmethod
    def modify_item(cls, id: int, data: dict) -> db.Table:
        data = cls._parse_image(data)
        return super().modify_item(id, data)

