"""
API resources for resource objects
"""

from typing import Optional

from flask import request
from flask_restful import Resource

from resource_allocator.managers.resource import (
    ResourceManager, ResourceGroupManager, ResourceToGroupModel,
)
from resource_allocator.schemas.response.resource import ResourceResponseSchema

class ResourceResource(Resource):
    def get(self, id: Optional[int] = None) -> dict:
        #   TODO: add auth
        if id is None:
            result = ResourceManager.list_all_items()
            return ResourceResponseSchema().dump(result, many = True)

        result = ResourceManager.list_single_item(id)
        return ResourceResponseSchema().dump(result)

    def post(self) -> dict:
        data = request.get_json()
        result = ResourceManager.create_item(data)
        return ResourceResponseSchema().dump(result)

