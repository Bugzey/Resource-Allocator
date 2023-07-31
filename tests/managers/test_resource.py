"""
Tests for managers.base
"""

import base64
from io import BytesIO
import unittest

from PIL import Image

from resource_allocator.config import Config
from resource_allocator.db import get_session
from resource_allocator.models import (
    metadata,
    populate_enums,
    ResourceGroupModel,
    ImageModel,
)
from resource_allocator.utils.db import change_schema
from resource_allocator.managers.resource import ResourceGroupManager

metadata = change_schema(metadata, "resource_allocator_test")


class ResourceGroupManagerTestCase(unittest.TestCase):
    """
    Note: this test only checks for nested image integration
    """
    def setUp(self):
        self.config = Config.from_environment()
        self.sess = get_session()
        self.engine = self.sess.bind
        metadata.create_all(self.engine)
        populate_enums(metadata, self.sess)

        self.image = self._make_image()
        self.data = {
            "name": "some group",
            "is_top_level": True,
            "image": {
                "image": self.image,
            },
        }

    def tearDown(self):
        self.sess.rollback()
        metadata.drop_all(self.engine)

    @staticmethod
    def _make_image(**args) -> bytes:
        args = {
            **dict(mode="L", size=(100, 100), color=0),
            **args,
        }
        with Image.new(**args) as image:
            image_bytes_io = BytesIO()
            image.save(image_bytes_io, format="png")
            image_bytes_io.seek(0)
            return base64.b64encode(image_bytes_io.read()).decode()

    def test_create_resource_group_with_image(self):
        result = ResourceGroupManager.create_item(self.data)
        self.assertTrue(isinstance(result, ResourceGroupModel))
        self.assertTrue(isinstance(result.image, ImageModel))

    def test_modify_resource_group_with_image(self):
        data = self.data.copy()  # mutability shenanigans
        original_result = ResourceGroupManager.create_item(data)
        original_image = original_result.image.image_data

        data = self.data.copy()  # mutability shenanigans
        data["image"] = {"image": self._make_image(color=255)}
        result = ResourceGroupManager.modify_item(original_result.id, data)
        self.assertTrue(isinstance(result, ResourceGroupModel))
        self.assertTrue(isinstance(result.image, ImageModel))

        self.assertEqual(len(self.sess.query(ImageModel).all()), 1)
        new_image = result.image.image_data
        self.assertNotEqual(original_image, new_image)
