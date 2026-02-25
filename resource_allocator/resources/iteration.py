"""
Resources for iteration objects
"""

from resource_allocator.schemas.iteration import (
    IterationRequestSchema, IterationResponseSchema,
)
from resource_allocator.managers.iteration import IterationManager
from resource_allocator.resources.base import CRUDResource


class IterationResource(CRUDResource):
    manager = IterationManager
    request_schema = IterationRequestSchema
    response_schema = IterationResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["admin"]
