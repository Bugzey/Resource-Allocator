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
from resource_allocator.resources.base import BaseResource, CRUDResource
from resource_allocator.managers.user import auth, role_required


class RequestResource(CRUDResource):
    manager = RequestManager
    request_schema = RequestRequestSchema
    response_schema = RequestResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["user", "admin"]


class RequestApproveResource(BaseResource):
    manager = RequestManager
    response_schema = RequestResponseSchema

    @auth.login_required
    @role_required("admin")
    def post(self, id: int) -> dict:
        return self.manager.approve(id)


class RequestDeclineResource(BaseResource):
    manager = RequestManager
    response_schema = RequestResponseSchema

    @auth.login_required
    @role_required("admin")
    def post(self, id: int) -> dict:
        return self.manager.decline(id)
