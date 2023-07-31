"""
Image resources
"""


from resource_allocator.managers.image import (
    ImageManager,
    ImagePropertiesManager,
)
from resource_allocator.schemas.image import (
    ImageRequestSchema,
    ImageResponseSchema,
    ImagePropertiesRequestSchema,
    ImagePropertiesResponseSchema,
)
from resource_allocator.resources.base import BaseResource


class ImageResource(BaseResource):
    manager = ImageManager
    request_schema = ImageRequestSchema
    response_schema = ImageResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["admin"]


class ImagePropertiesResource(BaseResource):
    manager = ImagePropertiesManager
    request_schema = ImagePropertiesRequestSchema
    response_schema = ImagePropertiesResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["admin"]
