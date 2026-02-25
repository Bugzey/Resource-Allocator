"""
Resources for allocation objects
"""

from flask import request

from resource_allocator.schemas.allocation import (
    AllocationRequestSchema, AllocationResponseSchema,
    AllocationAutomaticAllocationSchema,
)
from resource_allocator.managers.allocation import AllocationManager
from resource_allocator.resources.base import BaseResource, CRUDResource
from resource_allocator.managers.user import auth, role_required


class AllocationResource(CRUDResource):
    manager = AllocationManager
    request_schema = AllocationRequestSchema
    response_schema = AllocationResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["admin"]


class AutoAllocationResource(BaseResource):
    manager = AllocationManager
    request_schema = AllocationAutomaticAllocationSchema
    response_schema = AllocationResponseSchema
    write_roles_required = ["admin"]

    @auth.login_required
    @role_required("admin")
    def post(self) -> dict:
        data = request.get_json()
        result = self.manager.automatic_allocation(
            AllocationAutomaticAllocationSchema().load(data)
        )
        return self.response_schema().dump(result, many=True)
