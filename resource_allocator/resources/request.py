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
from resource_allocator.resources.base import BaseResource, CRUDResource, auth, role_required


class RequestResource(CRUDResource):
    manager_class = RequestManager
    request_schema = RequestRequestSchema
    response_schema = RequestResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["user", "admin"]


class RequestApproveResource(BaseResource):
    manager_class = RequestManager
    response_schema = RequestResponseSchema

    @auth.login_required
    @role_required("admin")
    @BaseResource.validate_schema(request_schema=None)
    def post(self, id: int, data: dict | None = None) -> dict:
        return self.manager.approve(id)


class RequestDeclineResource(BaseResource):
    manager_class = RequestManager
    response_schema = RequestResponseSchema

    @auth.login_required
    @role_required("admin")
    @BaseResource.validate_schema(request_schema=None)
    def post(self, id: int, data: dict | None = None) -> dict:
        return self.manager.decline(id)
