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
    def approve(cls, id: int, create_allocation: bool = True) -> RequestModel:
        """
        Approve and allocate a single request

        Args:
            id: request id

        Returns:
            The created RequestModel object
        """
        #   Create an allocation - auto allocation if requesting a group, specific resource
        #   otherwise
        request = cls.list_single_item(id)
        allocation_manager = cls._get_allocation_manager()

        if (
            create_allocation
            and request.requested_resource_group_id
            and not request.requested_resource_id
        ):
            allocation_manager.automatic_allocation({
                "iteration_id": request.iteration_id,
                "request_id": request.id,
            })

        elif create_allocation:
            allocation_manager.create_item(
                data={
                    "date": request.requested_date,
                    "iteration_id": request.iteration_id,
                    "allocated_resource_id": request.requested_resource_id,
                    "user_id": request.user_id,
                    "source_request_id": request.id,
                },
                approve_request=False,
            )

        #   Change status to approved
        status_id = cls.sess.scalar(
            select(RequestStatusModel.id)
            .where(RequestStatusModel.request_status == RequestStatusEnum.completed.value)
        )
        request: RequestModel = super().modify_item(
            id,
            {"request_status_id": status_id},
        )
        cls.sess.refresh(request)
        return request

    @classmethod
    def decline(cls, id: int, delete_allocation: bool = True) -> RequestModel:
        #   Change status to declined
        status_id = cls.sess.scalar(
            select(RequestStatusModel.id)
            .where(RequestStatusModel.request_status == RequestStatusEnum.declined.value)
        )
        request: RequestModel = super().modify_item(
            id,
            {"request_status_id": status_id},
        )
        cls.sess.refresh(request)

        #   Delete allocation if it exists
        if not delete_allocation:
            return request

        if request.allocation is not None:
            allocation_manager = cls._get_allocation_manager()
            allocation_manager.delete_item(id=request.allocation.id)

        cls.sess.refresh(request)
        return request

    @classmethod
    def create_item(cls, data: dict) -> RequestModel:
        if "request_status_id" not in data:
            query = (
                select(RequestStatusModel.id)
                .where(RequestStatusModel.request_status == RequestStatusEnum.new.value)
            )
            data["request_status_id"] = cls.sess.execute(query).scalar()

        request: RequestModel = super().create_item(data)

        #   Automatically allocate if the iteration has been allocated
        if request.iteration.is_allocated:
            allocation_manager = cls._get_allocation_manager()
            allocation_manager.automatic_allocation({
                "iteration_id": request.iteration_id,
                "request_id": request.id,
            })

        return request

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
            manager.delete_item(request.allocation.id)

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
        request: RequestModel = super().modify_item(id, data)
        if request.allocation is not None:
            cls.decline(request.id)

        if request.iteration.is_allocated:
            allocation_manager = cls._get_allocation_manager()
            allocation_manager.automatic_allocation({
                "iteration_id": request.iteration_id,
                "request_id": request.id,
            })

        cls.sess.refresh(request)
        return request
