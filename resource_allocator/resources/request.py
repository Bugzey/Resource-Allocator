"""
API resources for request objects
"""

from resource_allocator.managers.request import (
    RequestManager,
)
from resource_allocator.schemas.request import (
    RequestRequestSchema,
    RequestResponseSchema,
)
from resource_allocator.resources.base import BaseResource


class RequestResource(BaseResource):
    manager = RequestManager
    request_schema = RequestRequestSchema
    response_schema = RequestResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["user", "admin"]
