"""
Tests for managers.base
"""

from io import BytesIO
import unittest
from unittest.mock import patch, MagicMock

from PIL import Image
import sqlalchemy as db
from sqlalchemy import (Column, Integer, String)
from sqlalchemy.orm import declarative_base

from resource_allocator.db import sess, engine
from resource_allocator.models import (
    metadata, Base, populate_enums, ResourceGroupModel, ResourceModel, ImageModel,
)
from resource_allocator.utils.db import change_schema
from resource_allocator.managers.resource import ResourceManager, ResourceGroupManager

metadata = change_schema(metadata, "resource_allocator_test")


class ResourceGroupManagerTestCase(unittest.TestCase):
    """
    Note: this test only checks for nested image integration
    """
    def setUp(self):
        metadata.create_all(engine)
        populate_enums(metadata, sess)

        self.image = self._make_image()
        self.data = {
            "name": "some group",
            "is_top_level": True,
            "image": {
                "image": self.image,
            },
        }

    def tearDown(self):
        sess.rollback()
        metadata.drop_all(engine)

    @staticmethod
    def _make_image(**args) -> bytes:
        args = {
            **dict(mode="L", size=(100, 100), color=0),
            **args,
        }
        with Image.new(**args) as image:
            image_bytes_io = BytesIO()
            image.save(image_bytes_io, format = "png")
            image_bytes_io.seek(0)
            return image_bytes_io.read()

    def test_create_resource_group_with_image(self):
        result = ResourceGroupManager.create_item(self.data)
        self.assertTrue(isinstance(result, ResourceGroupModel))
        self.assertTrue(isinstance(result.image, ImageModel))

    def test_modify_resource_group_with_image(self):
        data = self.data.copy() # mutability shenanigans
        original_result = ResourceGroupManager.create_item(data)
        original_image = original_result.image.image_data

        data = self.data.copy() # mutability shenanigans
        data["image"] = {"image": self._make_image(color = 255)}
        result = ResourceGroupManager.modify_item(original_result.id, data)
        self.assertTrue(isinstance(result, ResourceGroupModel))
        self.assertTrue(isinstance(result.image, ImageModel))

        self.assertEqual(len(sess.query(ImageModel).all()), 1)
        new_image = result.image.image_data
        self.assertNotEqual(original_image, new_image)

