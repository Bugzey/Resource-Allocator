"""
Allocation manager
"""

import sqlalchemy as db
from sqlalchemy import select

from resource_allocator.models import (
    AllocationModel,
    IterationModel,
    ResourceModel,
    RequestModel,
    RequestStatusEnum,
    RequestStatusModel,
)
from resource_allocator.managers.base import BaseManager
from resource_allocator.managers.iteration import IterationManager
from resource_allocator.managers.request import RequestManager


class AllocationManager(BaseManager):
    model = AllocationModel

    @classmethod
    def create_item(cls, data: dict) -> db.Table:
        """
        Create allocation and set status to completed
        """
        allocation: AllocationModel = super().create_item(data)
        sess = cls.sess

        request_completed_id = sess.scalar(
            select(RequestStatusModel.id)
            .where(RequestStatusModel.request_status == RequestStatusEnum.completed.value)
        )
        RequestManager.modify_item(
            allocation.source_request_id,
            {"request_status_id": request_completed_id}
        )
        return allocation

    @classmethod
    def _assign_points(cls, request: RequestModel, resource: ResourceModel) -> int:
        points = 0

        #   If this is the exact resource being requested, add 2 points
        points += 2 * (request.requested_resource == resource)

        #   If the resource's groups and the request groups overlap,
        #   add 10 points
        points += 10 * (
            request.requested_resource is not None
            and (
                set(request.requested_resource.resource_groups)
                & set(resource.resource_groups) != set()
            )
        )
        points += 10 * (
            request.requested_resource_group_id in [
                item.id
                for item
                in resource.resource_groups
            ]
        )

        #   Add some points if located in the same top-level resource group
        points += 5 * (
            (
                request.requested_resource is not None
                and request.requested_resource.top_resource_group_id ==
                resource.top_resource_group_id
            )
            or (
                request.requested_resource is None
                and request.requested_resource_group.top_resource_group_id ==
                resource.top_resource_group_id
            )
        )
        #   If a user has been granted this resource in the previous day's alloaction,
        #   add an extra 2 points
        #   TODO

        return points

    @classmethod
    def _remove_requests(
        cls,
        request: RequestModel,
        resource: ResourceModel,
        points: dict[tuple[RequestModel, ResourceModel], int],
    ):
        new_points = {}
        for (points_request, points_resource), value in points.items():
            points_request: RequestModel
            points_resource: ResourceModel

            if points_resource.id == resource.id:
                continue

            if (
                points_request.requested_resource_id is not None
                and points_request.user_id == request.user_id
                and points_request.requested_resource.top_resource_group_id ==
                resource.top_resource_group_id
            ):
                continue

            if (
                points_request.requested_resource_group_id is not None
                and points_request.user_id == request.user_id
                and points_request.requested_resource_group.top_resource_group_id ==
                resource.top_resource_group_id
            ):
                continue

            new_points[(points_request, points_resource)] = value

        return new_points

    @classmethod
    def automatic_allocation(cls, data: dict) -> list[AllocationModel]:
        """
        Generate optimal allocations of resources to users to dates based on requests sent by the
        users priod to the allocation
        """
        #   Get the iteration being worked on and associated requests
        iteration = cls.sess.get(IterationModel, data["iteration_id"])
        all_resources = cls.sess.query(ResourceModel).all()
        request_declined_id = cls.sess.scalar(
            select(RequestStatusModel.id)
            .where(RequestStatusModel.request_status == RequestStatusEnum.declined.value)
        )

        #   Handle all requests or a single request
        if "request_id" in data:
            all_requests = [RequestManager.list_single_item(data["request_id"])]
        else:
            all_requests = iteration.requests

        #   Loop over each day of the iteration
        all_dates = sorted(list({
            request.requested_date for request in all_requests
        }))
        allocation = dict()

        for date in all_dates:
            requests = [
                request
                for request
                in iteration.requests
                if request.requested_date == date
            ]
            points = dict()

            #   Loop over each resource
            for resource in all_resources:

                #   Assign user points
                for request in requests:
                    key = (request, resource)
                    points[key] = cls._assign_points(request, resource)

            allocation[date] = []

            while points:
                max_points = max(points.values())
                cur_allocation = next(
                    (key for key, value in points.items() if value == max_points and value > 0),
                    None,
                )
                if not cur_allocation:
                    break

                request, resource = cur_allocation
                allocation[date].append({
                    "allocated_resource_id": resource.id,
                    "user_id": request.user_id,
                    "points": max_points,
                    "source_request_id": request.id,
                })

                #   Set request status - handled below by cls.create_item

                #   Remove resource and user requests for the same top resource group id
                points = cls._remove_requests(request, resource, points)

        #   Add the allocations using the post interface
        result = []
        for date, allocation_list in allocation.items():
            result.extend([
                cls.create_item({
                    **item,
                    "date": date,
                    "iteration_id":
                    iteration.id
                }) for item in allocation_list
            ])

        #   Decline leftover requests
        fulfilled_request_ids = [item.source_request_id for item in result]
        leftover = [item for item in iteration.requests if item.id not in fulfilled_request_ids]
        for item in leftover:
            RequestManager.modify_item(item.id, {"request_status_id": request_declined_id})

        #   Close iteration for new requests
        IterationManager.modify_item(iteration.id, {"is_allocated": True})

        return result
