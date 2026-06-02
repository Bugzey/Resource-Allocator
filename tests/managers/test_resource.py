"""
Tests for managers.base
"""

import base64
from io import BytesIO
import unittest

from PIL import Image

from resource_allocator.models import (
    ResourceGroupModel,
    ImageModel,
)
from resource_allocator.managers.resource import ResourceGroupManager

from tests.managers.test_base import TestBase


class ResourceGroupManagerTestCase(TestBase, unittest.TestCase):
    """
    Note: this test only checks for nested image integration
    """
    def setUp(self):
        super().setUp()
        self.image = self._make_image()
        self.data = {
            "name": "some group",
            "is_top_level": True,
            "image": {
                "image": self.image,
            },
        }

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
        result = ResourceGroupManager(self.sess).create_item(self.data)
        self.assertTrue(isinstance(result, ResourceGroupModel))
        self.assertTrue(isinstance(result.image, ImageModel))

    def test_modify_resource_group_with_image(self):
        data = self.data.copy()  # mutability shenanigans
        original_result = ResourceGroupManager(self.sess).create_item(data)
        original_image = original_result.image.image_data

        data = self.data.copy()  # mutability shenanigans
        data["image"] = {"image": self._make_image(color=255)}
        result = ResourceGroupManager(self.sess).modify_item(original_result.id, data)
        self.assertTrue(isinstance(result, ResourceGroupModel))
        self.assertTrue(isinstance(result.image, ImageModel))

        self.assertEqual(len(self.sess.query(ImageModel).all()), 1)
        new_image = result.image.image_data
        self.assertNotEqual(original_image, new_image)
