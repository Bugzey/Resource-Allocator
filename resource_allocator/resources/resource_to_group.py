"""
API resources for resource to group
"""

from resource_allocator.resources.base import BaseResource
from resource_allocator.managers.resource_to_group import ResourceToGroupManager
from resource_allocator.schemas.resource_to_group import (
    ResourceToGroupRequestSchema, ResourceToGroupResponseSchema,
)


class ResourceToGroupResource(BaseResource):
    manager = ResourceToGroupManager
    request_schema = ResourceToGroupRequestSchema
    response_schema = ResourceToGroupResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["admin"]
