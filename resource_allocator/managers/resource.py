"""
Managers for working with resources
"""

from resource_allocator.models import (
    ResourceModel,
    ResourceGroupModel,
    ResourceToGroupModel,
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

    def create_item(self, data: dict) -> ResourceGroupModel:
        result = super().create_item(data)
        if not data["is_top_level"]:
            return result

        result.top_resource_group_id = result.id
        self.sess.flush()
        return result


class ResourceToResourceGroupManager(BaseManager):
    model = ResourceToGroupModel
