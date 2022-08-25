"""
API resources for resource objects
"""

from typing import Optional

from flask import request

from resource_allocator.db import sess
from resource_allocator.managers.user import auth
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
        result = self.manager.modify_item(id, self.request_schema().dump(data))
        return self.response_schema().dump(result)

