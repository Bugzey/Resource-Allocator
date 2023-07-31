"""
Iteration-related managers
"""

from resource_allocator.models import IterationModel
from resource_allocator.managers.base import BaseManager


class IterationManager(BaseManager):
    model = IterationModel
