"""
Allocation manager
"""

from typing import Optional

import sqlalchemy as db

from resource_allocator.models import (
    AllocationModel,
    IterationModel,
    ResourceModel,
)
from resource_allocator.managers.base import BaseManager
from resource_allocator.managers.iteration import IterationManager


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
        all_resorces = cls.sess.query(ResourceModel).all()

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
            for resource in all_resorces:
                #   Assign user points
                for request in requests:
                    key = (resource.id, request.user_id, request.id)
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
                    #   If a user has been granted this resource in the previous day's alloaction,
                    #   add an extra 2 points
                    #   TODO

            allocation[date] = []
            while points:
                max_points = max(points.values())
                cur_allocation = [
                    key for key, value in points.items() if value == max_points
                ][0]
                resource_id, user_id, request_id = cur_allocation
                allocation[date].append({
                    "allocated_resource_id": resource_id,
                    "user_id": user_id,
                    "points": max_points,
                    "source_request_id": request_id,
                })
                points = {key: value for key, value in points.items() if key[0] != resource_id}

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

        #   Close iteration for new requests
        IterationManager.modify_item(iteration.id, {"accepts_requests": False})

        return result
