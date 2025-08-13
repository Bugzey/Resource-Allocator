"""
Request-related managers
"""

from sqlalchemy import select

from resource_allocator.models import (
    RequestModel,
    RequestStatusEnum,
    RequestStatusModel,
    IterationModel,
)
from resource_allocator.managers.base import BaseManager
from resource_allocator.managers.iteration import IterationManager


class RequestManager(BaseManager):
    model = RequestModel

    @classmethod
    def create_item(cls, data: dict):
        if "request_status_id" not in data:
            query = (
                select(RequestStatusModel.id)
                .where(RequestStatusModel.request_status == RequestStatusEnum.new.value)
            )
            data["request_status_id"] = cls.sess.execute(query).scalar()

        result = super().create_item(data)

        #   Automatically allocate if the iteration has been allocated
        iteration: IterationModel = IterationManager.list_single_item(data["iteration_id"])
        if iteration.is_allocated:
            from resource_allocator.managers.allocation import AllocationManager
            _ = AllocationManager.automatic_allocation({
                "iteration_id": iteration.id,
                "request_id": result.id,
            })
            cls.sess.refresh(result)
        return result
