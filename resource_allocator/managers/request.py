"""
Request-related managers
"""

from resource_allocator.models import RequestModel
from resource_allocator.managers.base import BaseManager

class RequestManager(BaseManager):
    model = RequestModel

