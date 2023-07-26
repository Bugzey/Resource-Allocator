"""
Managers for working with resources
"""

import sqlalchemy as db

from resource_allocator.models import (
    ResourceModel, ResourceGroupModel, ResourceToGroupModel,
)

from resource_allocator.managers.base import BaseManager
from resource_allocator.managers.image import ImageManager


class ResourceManager(BaseManager):
    model = ResourceModel
    nested_managers = {
        "image": ImageManager,
    }


class ResourceGroupManager(BaseManager):
    model = ResourceGroupModel
    nested_managers = {
        "image": ImageManager,
    }


class ResourceToResourceGroupManager(BaseManager):
    model = ResourceToGroupModel
