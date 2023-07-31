"""
Managers for working with resources
"""

from resource_allocator.models import (
    ResourceModel, ResourceGroupModel, ResourceToGroupModel,
)

from resource_allocator.managers.base import BaseManager
from resource_allocator.managers.image import (
    ImageManager,
    ImagePropertiesManager,
)


class ResourceManager(BaseManager):
    model = ResourceModel
    nested_managers = {
        "image": ImageManager,
        "image_properties": ImagePropertiesManager,
    }


class ResourceGroupManager(BaseManager):
    model = ResourceGroupModel
    nested_managers = {
        "image": ImageManager,
        "image_properties": ImagePropertiesManager,
    }


class ResourceToResourceGroupManager(BaseManager):
    model = ResourceToGroupModel
