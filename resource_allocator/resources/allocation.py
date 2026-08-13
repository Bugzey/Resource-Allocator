"""
Resources for allocation objects
"""

from resource_allocator.schemas.allocation import (
    AllocationRequestSchema, AllocationResponseSchema,
    AllocationAutomaticAllocationSchema,
)
from resource_allocator.managers.allocation import AllocationManager
from resource_allocator.resources.base import BaseResource, CRUDResource, auth, role_required


class AllocationResource(CRUDResource):
    manager_class = AllocationManager
    request_schema = AllocationRequestSchema
    response_schema = AllocationResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["admin"]


class AutoAllocationResource(BaseResource):
    manager_class = AllocationManager
    request_schema = AllocationAutomaticAllocationSchema
    response_schema = AllocationResponseSchema
    write_roles_required = ["admin"]

    @auth.login_required
    @role_required("admin")
    @BaseResource.validate_schema()
    def post(self, data: dict | None = None) -> dict:
        result = self.manager.automatic_allocation(
            AllocationAutomaticAllocationSchema().load(data)
        )
        return result
