"""
Image manager
"""

import base64
from io import BytesIO

import sqlalchemy as db
from PIL import Image

from resource_allocator.models import (
    ImageModel,
    ImagePropertiesModel,
    ImageTypeModel,
)
from resource_allocator.managers.base import BaseManager


class ImageTypeManager(BaseManager):
    model = ImageTypeModel


class ImageManager(BaseManager):
    model = ImageModel

    def _parse_image(self, data: dict) -> dict:
        with Image.open(BytesIO(data["image"])) as image:
            image_type = image.format
            image_type_id = self.sess \
                .query(ImageTypeModel.id) \
                .where(ImageTypeModel.image_type == image_type) \
                .scalar()

            if not image_type_id:
                new_image_type = ImageTypeModel(image_type=image_type)
                self.sess.add(new_image_type)
                self.sess.flush()
                image_type_id = new_image_type.id

        return {
            "image_data": data["image"],
            "image_type_id": image_type_id,
            "size_bytes": len(data["image"]),
        }

    def create_item(self, data: dict) -> db.Table:
        data["image"] = base64.b64decode(data["image"])
        data = self._parse_image(data)
        return super().create_item(data)

    def modify_item(self, id: int, data: dict) -> db.Table:
        data["image"] = base64.b64decode(data["image"])
        data = self._parse_image(data)
        return super().modify_item(id, data)

    def list_single_item(self, id: int) -> db.Table:
        item = super().list_single_item(id)
        if not isinstance(item, self.model):
            return item

        item.__dict__["image"] = base64.b64encode(item.image_data).decode()
        return item


class ImagePropertiesManager(BaseManager):
    model = ImagePropertiesModel
