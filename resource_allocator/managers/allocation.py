"""
Allocation manager
"""

from typing import Optional

import sqlalchemy as db

from resource_allocator.db import sess
from resource_allocator.models import AllocationModel, IterationModel
from resource_allocator.managers.base import BaseManager

class AllocationManager(BaseManager):
    model = AllocationModel

    @classmethod
    def automatic_allocation(cls, data: Optional[dict]) -> list[db.Table]:
        """
        Generate optimal allocations of resources to users to dates based on requests sent by the
        users priod to the allocation
        """
        #   Get the iteration being worked on and associated requests
        iteration = sess.get(IterationModel, data["iteration_id"])

        #   Loop over each day of the iteration
        all_dates = sorted(list({
            request.requested_date for request in iteration.requests
        }))
        for date in all_dates:
            requests = [
                request for request in iteration.requests \
                if request.requested_date == date
            ]
            breakpoint()

        #   Loop over each resource

        #   Assign user points for being granted the resource - split 10 points evenly among the
        #   requested resource and each parent resource group

        #   If a user has been granted this resource in the previous day's alloaction,
        #   add an extra 2 points

        #   If this is the exact resource being requested, add 2 points
        pass

