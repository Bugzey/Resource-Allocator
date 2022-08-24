"""
API resources for resource objects
"""

from typing import Optional

from resource_allocator.managers.resource import (
    ResourceManager, ResourceGroupManager, ResourceToGroupModel,
)
from resource_allocator.schemas.response.resource import (
    ResourceResponseSchema, ResourceGroupResponseSchema,
)
from resource_allocator.schemas.request.resource import (
    ResourceRequestSchema, ResourceGroupRequestSchema,
)
from resource_allocator.resources.base import BaseResource

class ResourceResource(BaseResource):
    manager = ResourceManager
    request_schema = ResourceRequestSchema
    response_schema = ResourceResponseSchema
    read_role_required = "user"
    write_role_required = "admin"


class ResourceGroupResource(BaseResource):
    manager = ResourceGroupManager
    request_schema = ResourceGroupRequestSchema
    response_schema = ResourceGroupResponseSchema
    read_role_required = "user"
    write_role_required = "admin"

