"""
Managers for working with resources
"""

import sqlalchemy as db

from resource_allocator.models import (
    ResourceModel, ResourceGroupModel, ResourceToGroupModel,
)

from resource_allocator.managers.base import BaseManager


class ResourceManager(BaseManager):
    model = ResourceModel


class ResourceGroupManager(BaseManager):
    model = ResourceGroupModel


class ResourceToResourceGroupManager(BaseManager):
    model = ResourceToGroupModel


