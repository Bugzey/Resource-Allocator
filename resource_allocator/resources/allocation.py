"""
Resources for allocation objects
"""

from flask import request

from resource_allocator.schemas.allocation import (
    AllocationRequestSchema, AllocationResponseSchema,
    AllocationAutomaticAllocationSchema,
)
from resource_allocator.managers.allocation import AllocationManager
from resource_allocator.resources.base import BaseResource
from resource_allocator.managers.user import auth, role_required


class AllocationResource(BaseResource):
    manager = AllocationManager
    request_schema = AllocationRequestSchema
    response_schema = AllocationResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["admin"]

    @auth.login_required
    @role_required("admin")
    def post(self):
        if "automatic_allocation" in request.path:
            data = request.get_json()
            errors = AllocationAutomaticAllocationSchema().validate(data)
            if errors:
                return "Data validation errors: {}".format(errors), 400

            result = self.manager.automatic_allocation(
                AllocationAutomaticAllocationSchema().load(data)
            )
            return self.response_schema().dump(result, many = True)

        return super().post()

