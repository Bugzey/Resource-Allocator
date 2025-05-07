"""
Unit tests for managers.image
"""

import base64
from io import BytesIO
import unittest

from PIL import Image

from resource_allocator import models
from resource_allocator.config import Config
from resource_allocator.db import get_session
from resource_allocator.managers.image import ImageManager
from resource_allocator.utils.db import change_schema

metadata = change_schema(models.metadata, schema="resource_allocator_test")


class ImageManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Config.from_environment()
        self.sess = get_session()
        self.engine = self.sess.bind
        metadata.create_all(self.engine)
        models.populate_enums(self.sess)

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
            return base64.b64encode(image_bytes_io.read())

    def tearDown(self):
        self.sess.rollback()
        metadata.drop_all(self.engine)

    def test_create(self):
        image = self._make_image()
        result = ImageManager.create_item(data={"image": image})
        self.assertIsNotNone(result.image_type_id)
        self.assertGreater(result.size_bytes, 0)

    def test_modify_item(self):
        initial_image = self._make_image()
        initial = ImageManager.create_item(data={"image": initial_image})
        initial_size = initial.size_bytes

        new_image = self._make_image(size=(128, 128))
        result = ImageManager.modify_item(initial.id, data={"image": new_image})
        result_size = result.size_bytes
        self.assertNotEqual(initial_size, result_size)

        self.assertEqual(len(self.sess.query(models.ImageModel).all()), 1)
