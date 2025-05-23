"""
API resources for resource objects
"""

from resource_allocator.managers.user import auth
from resource_allocator.managers.resource import (
    ResourceManager,
    ResourceGroupManager,
)
from resource_allocator.schemas.resource import (
    ResourceRequestSchema,
    ResourceResponseSchema,
)
from resource_allocator.schemas.resource_group import (
    ResourceGroupRequestSchema,
    ResourceGroupResponseSchema,
)
from resource_allocator.resources.base import BaseResource


class ResourceResource(BaseResource):
    manager = ResourceManager
    request_schema = ResourceRequestSchema
    response_schema = ResourceResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["admin"]


class ResourceGroupResource(BaseResource):
    manager = ResourceGroupManager
    request_schema = ResourceGroupRequestSchema
    response_schema = ResourceGroupResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["admin"]

    @auth.login_required
    def post(self):
        data = super().post()
        if isinstance(data, tuple) or not data["is_top_level"]:
            return data

        id = data["id"]
        data["top_resource_group_id"] = id
        result = self.manager.modify_item(id, {"top_resource_group_id": id})
        return self.response_schema().dump(result)
