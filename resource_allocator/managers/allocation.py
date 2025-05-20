"""
Allocation manager
"""

from typing import Optional

import sqlalchemy as db

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
    def automatic_allocation(cls, data: Optional[dict]) -> list[db.Table]:
        """
        Generate optimal allocations of resources to users to dates based on requests sent by the
        users priod to the allocation
        """
        #   Get the iteration being worked on and associated requests
        iteration = cls.sess.get(IterationModel, data["iteration_id"])
        all_resources = cls.sess.query(ResourceModel).all()
        request_status = cls.sess.query(RequestStatusModel).all()
        request_completed_id = next(
            item.id
            for item
            in request_status
            if item.request_status == RequestStatusEnum.completed.value
        )
        request_declined_id = next(
            item.id
            for item
            in request_status
            if item.request_status == RequestStatusEnum.declined.value
        )

        #   Loop over each day of the iteration
        all_dates = sorted(list({
            request.requested_date for request in iteration.requests
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
                resource: ResourceModel
                #   Assign user points
                for request in requests:
                    request: RequestModel
                    key = (request, resource)
                    points[key] = 0

                    #   If this is the exact resource being requested, add 2 points
                    points[key] += 2 * (request.requested_resource == resource)

                    #   If the resource's groups and the request groups overlap,
                    #   add 10 points
                    points[key] += 10 * (
                        request.requested_resource is not None
                        and (
                            set(request.requested_resource.resource_groups)
                            & set(resource.resource_groups) != set()
                        )
                    )
                    points[key] += 10 * (
                        request.requested_resource_group_id in [
                            item.id
                            for item
                            in resource.resource_groups
                        ]
                    )

                    #   Add some points if located in the same top-level resource group
                    points[key] += 5 * (
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

            allocation[date] = []
            while points:
                max_points = max(points.values())
                cur_allocation = next(
                    (key for key, value in points.items() if value == max_points and value > 0),
                    None,
                )
                if not cur_allocation:
                    break

                if request.id == 3:
                    breakpoint()

                request, resource = cur_allocation
                allocation[date].append({
                    "allocated_resource_id": resource.id,
                    "user_id": request.user_id,
                    "points": max_points,
                    "source_request_id": request.id,
                })

                #   Set request status
                RequestManager.modify_item(
                    request.id,
                    {"request_status_id": request_completed_id}
                )

                #   Remove resource and user requests for the same top resource group id
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

                points = new_points

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
        IterationManager.modify_item(iteration.id, {"accepts_requests": False})

        return result
