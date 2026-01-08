"""
Request-related managers
"""

from sqlalchemy import select

from resource_allocator.models import (
    RequestModel,
    RequestStatusEnum,
    RequestStatusModel,
)
from resource_allocator.managers.base import BaseManager


class RequestManager(BaseManager):
    model = RequestModel

    @staticmethod
    def _get_allocation_manager() -> BaseManager:
        from resource_allocator.managers.allocation import AllocationManager
        return AllocationManager

    @classmethod
    def _run_allocation_if_needed(cls, request: RequestModel):
        iteration = request.iteration
        if not iteration.is_allocated:
            return request

        manager = cls._get_allocation_manager()

        #   Delete old allocation
        if request.allocation:
            manager.delete_item(request.allocation.id, decline_request=False)

        #   Run an automatic allocation
        manager.automatic_allocation({
            "iteration_id": iteration.id,
            "request_id": request.id,
        })
        cls.sess.refresh(request)
        return request

    @classmethod
    def approve(cls, id: int) -> RequestModel:
        status_id = cls.sess.scalar(
            select(RequestStatusModel.id)
            .where(RequestStatusModel.request_status == RequestStatusEnum.completed.value)
        )
        result = super().modify_item(
            id,
            {"request_status_id": status_id},
        )
        cls.sess.refresh(result)
        return result

    @classmethod
    def decline(cls, id: int) -> RequestModel:
        status_id = cls.sess.scalar(
            select(RequestStatusModel.id)
            .where(RequestStatusModel.request_status == RequestStatusEnum.declined.value)
        )
        result = super().modify_item(
            id,
            {"request_status_id": status_id},
        )
        cls.sess.refresh(result)
        return result

    @classmethod
    def create_item(cls, data: dict) -> RequestModel:
        if "request_status_id" not in data:
            query = (
                select(RequestStatusModel.id)
                .where(RequestStatusModel.request_status == RequestStatusEnum.new.value)
            )
            data["request_status_id"] = cls.sess.execute(query).scalar()

        result = super().create_item(data)

        #   Automatically allocate if the iteration has been allocated
        result = cls._run_allocation_if_needed(result)
        return result

    @classmethod
    def delete_item(cls, id: int) -> RequestModel:
        """
        Delete a request. If an allocation exists for this request, then it is also deleted

        Args:
            id: request identifier

        Returns:
            Model for the deleted row
        """
        request: RequestModel = cls.list_single_item(id)
        if request.allocation is not None:
            manager = cls._get_allocation_manager()
            manager.delete_item(request.allocation.id, decline_request=False)

        return super().delete_item(id)

    @classmethod
    def modify_item(cls, id: int, data: dict) -> RequestModel:
        """
        Modify a request. If an allocation exists for this request, then it is deleted and automatic
        allocation is run

        Args:
            id: request identifier
            data: new data

        Returns:
            Model for the deleted row
        """
        result = cls.decline(id)
        result = super().modify_item(result.id, data)
        result = cls._run_allocation_if_needed(result)
        return result
