"""
Iteration-related managers
"""

from resource_allocator.models import ResourceToGroupModel
from resource_allocator.managers.base import BaseManager

class ResourceToGroupManager(BaseManager):
    model = ResourceToGroupModel

