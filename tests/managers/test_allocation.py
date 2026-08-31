"""
Unit tests for managers.allocation
"""

import datetime as dt
import unittest
from unittest.mock import MagicMock

from resource_allocator.config import Config
from resource_allocator.managers.base import Filter
from resource_allocator.managers.allocation import AllocationManager
from resource_allocator.managers.iteration import IterationManager
from resource_allocator.managers.request import RequestManager
from resource_allocator.managers.resource import ResourceManager, ResourceGroupManager
from resource_allocator.managers.resource_to_group import ResourceToGroupManager
from resource_allocator.managers.user import AuthManager, UserManager
from resource_allocator.models import (
    AllocationModel, IterationModel, RequestStatusEnum, RequestModel,
)

from tests.managers.test_base import TestBase


class AllocationManagerTestCase(TestBase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.config = MagicMock(
            spec=Config,
            AZURE_CONFIGURED=True,
            LOCAL_LOGIN_ENABLED=True,
            SECRET="asdf1234" * 8,
            TENANT_ID="TENANT_ID",
            REDIRECT_URI="http://REDIRECT_URI",
            ALLOWED_ORIGINS=["http://localhost"],
        )
        self.users_data = [
            {
                "email": "user1@example.com",
                "password": 123456,
                "first_name": "bla",
                "last_name": "bla",
            },
            {
                "email": "user2@example.com",
                "password": 123456,
                "first_name": "bla",
                "last_name": "bla",
            },
            {
                "email": "user3@example.com",
                "password": 123456,
                "first_name": "bla",
                "last_name": "bla",
            },
        ]
        self.auth_manager = AuthManager(self.sess, config=self.config)
        self.user_manager = UserManager(self.sess)

        _ = [self.auth_manager.register(user) for user in self.users_data]
        self.users = self.user_manager.list_all_items()

        self.resource_groups_data = [
            {
                "name": "top_level",
                "is_top_level": True,
            },
            {
                "name": "front_office",
                "is_top_level": False,
                "top_resource_group_id": 1,
            },
            {
                "name": "back_office",
                "is_top_level": False,
                "top_resource_group_id": 1,
            },
            {
                "name": "other_top_level",
                "is_top_level": True,
            },
        ]
        self.resource_group_manager = ResourceGroupManager(self.sess)
        self.resource_groups = [
            self.resource_group_manager.create_item(item)
            for item
            in self.resource_groups_data
        ]

        self.resources_data = [
            {
                "name": "desk1",
                "top_resource_group_id": 1,
            },
            {
                "name": "desk2",
                "top_resource_group_id": 1,
            },
            {
                "name": "desk_other_1",
                "top_resource_group_id": 4,
            },
            {
                "name": "desk_other_2",
                "top_resource_group_id": 4,
            },
        ]
        self.resource_manager = ResourceManager(self.sess)
        self.resources = [
            self.resource_manager.create_item(item)
            for item
            in self.resources_data
        ]

        self.resource_to_group = [
            {
                "resource_id": 1,
                "resource_group_id": 2,
            },
            {
                "resource_id": 2,
                "resource_group_id": 3,
            },
        ]
        self.resource_to_group_manager = ResourceToGroupManager(self.sess)
        [self.resource_to_group_manager.create_item(item) for item in self.resource_to_group]

        self.iteration_manager = IterationManager(self.sess)
        self.iteration = self.iteration_manager.create_item({
            "start_date": dt.date(2020, 1, 1),
            "end_date": dt.date(2020, 1, 7),
            "is_allocated": False,
        })

        self.request_date = dt.date(2020, 1, 1)
        self.requests_data = [
            {
                "iteration_id": 1,
                "requested_date": self.request_date,
                "user_id": 1,
                "requested_resource_id": 1,
            },
            {
                "iteration_id": 1,
                "requested_date": self.request_date,
                "user_id": 2,
                "requested_resource_group_id": 3,
            },
            {
                "iteration_id": 1,
                "requested_date": self.request_date,
                "user_id": 3,
                "requested_resource_group_id": 3,
            },  # Declined since no more resources are available
            {
                "iteration_id": 1,
                "requested_date": self.request_date,
                "user_id": 1,
                "requested_resource_group_id": 4,
            },  # User 1 requests a resource in a different top resource group id
        ]
        self.request_manager = RequestManager(self.sess)
        self.requests = [self.request_manager.create_item(item) for item in self.requests_data]

        self.allocation_args = {
            "iteration_id": 1,
        }
        self.allocation_manager = AllocationManager(self.sess)

    def test_create_item(self):
        result = self.allocation_manager.create_item(
            data=dict(
                iteration_id=self.iteration.id,
                date=dt.date(2020, 1, 1),
                user_id=self.users[0].id,
                user_for_id=self.users[0].id,
                allocated_resource_id=self.resources[0].id,
                source_request_id=self.requests[0].id,
            )
        )
        self.assertIsInstance(result, AllocationModel)

        #   Check that the source request is completed
        request: RequestModel = self.requests[0]
        self.assertEqual(request.request_status.request_status, RequestStatusEnum.completed.value)

    def test_delete_item(self):
        result = self.allocation_manager.create_item(
            data=dict(
                iteration_id=self.iteration.id,
                date=dt.date(2020, 1, 1),
                user_id=self.users[0].id,
                user_for_id=self.users[0].id,
                allocated_resource_id=self.resources[0].id,
                source_request_id=self.requests[0].id,
            )
        )
        self.assertIsInstance(result, AllocationModel)

        #   Delete the allocation
        self.allocation_manager.delete_item(result.id)

        #   Check that the source request is completed
        request: RequestModel = self.requests[0]
        self.assertEqual(request.request_status.request_status, RequestStatusEnum.declined.value)

    def test_automatic_allocation(self):
        result = self.allocation_manager.automatic_allocation(self.allocation_args)
        self.assertTrue(isinstance(result, list))

        #   Result is written to the database
        self.assertEqual(self.sess.query(AllocationModel).all(), result)

        #   Iteration is now closed for requests
        self.assertTrue(self.sess.get(IterationModel, 1).is_allocated)

        #   Request statuses
        requests = self.request_manager.list_all_items()
        requests.sort(key=lambda x: x.id)
        self.assertEqual(
            requests[0].request_status.request_status,
            RequestStatusEnum.completed.value,
        )
        self.assertEqual(
            requests[1].request_status.request_status,
            RequestStatusEnum.completed.value,
        )
        self.assertEqual(
            requests[2].request_status.request_status,
            RequestStatusEnum.declined.value,
        )
        self.assertEqual(
            requests[3].request_status.request_status,
            RequestStatusEnum.completed.value,
        )

        #   Run again - old requests should not get new allocations
        new = self.allocation_manager.automatic_allocation(self.allocation_args)
        self.assertTrue(isinstance(new, list))
        self.assertEqual(len(new), 0)
        self.assertEqual(len(self.allocation_manager.list_all_items()), len(result))

    def test_automatic_allocation_with_previous_manual_allocation(self):
        """
        An allocation was created before an automatic allocation run. The process should decline any
        active requests and otherwise ignore the allocated seat
        """
        #   User ID 1 gets resource.id=2 approved before tha auto allocation
        self.allocation_manager.create_item({
            "iteration_id": self.iteration.id,
            "date": dt.date(2020, 1, 1),
            "user_id": self.users[0].id,
            "user_for_id": self.users[0].id,
            "allocated_resource_id": self.resources[1].id,
            "source_request_id": self.requests[0].id,
        })
        self.sess.refresh(self.iteration)
        self.assertFalse(self.iteration.is_allocated)
        allocations = self.allocation_manager.list_all_items()
        self.assertEqual(len(allocations), 1)
        self.assertEqual(
            allocations[0].allocated_resource_id,
            self.resources[1].id,
            "Requested resource given despite manual allocation of different resource",
        )

        #   Run automatic allocation - request id above not sepcified, so there should be 2
        #   allocations
        _ = self.allocation_manager.automatic_allocation(self.allocation_args)
        self.sess.flush()
        user_1_allocations = self.allocation_manager.list_all_items(
            filters=[Filter("user_id", self.users[0].id), Filter("date", self.request_date)],
        )
        self.assertEqual(len(user_1_allocations), 2, "User 1 has multiple allocations for one date")

    def test_request_resource_after_allocation(self):
        _ = self.allocation_manager.automatic_allocation(self.allocation_args)

        #   New request to a free resource
        request = self.request_manager.create_item(
            {
                "iteration_id": 1,
                "requested_date": dt.date(2020, 1, 2),
                "user_id": 1,
                "requested_resource_id": 3,
            },
        )

        self.assertIsNotNone(request.id)
        allocated_resource = request.allocation
        self.assertIsNotNone(allocated_resource)
        self.assertEqual(allocated_resource.allocated_resource_id, 3)
        self.assertEqual(
            request.request_status.request_status,
            RequestStatusEnum.completed.value,
        )

        #   New request to a busy resource - should get a different free resource in the same group
        request = self.request_manager.create_item(
            {
                "iteration_id": 1,
                "requested_date": dt.date(2020, 1, 2),
                "user_id": 2,
                "requested_resource_id": 3,
            },
        )
        allocated_resource = request.allocation
        self.assertIsNotNone(allocated_resource)
        self.assertEqual(allocated_resource.allocated_resource_id, 4)
        self.sess.refresh(request)
        self.assertEqual(
            request.request_status.request_status,
            RequestStatusEnum.completed.value,
        )

        #   New request when no resources are free
        request = self.request_manager.create_item(
            {
                "iteration_id": 1,
                "requested_date": dt.date(2020, 1, 2),
                "user_id": 3,
                "requested_resource_id": 3,
            },
        )
        allocated_resource = request.allocation
        self.assertIsNone(allocated_resource)
        self.sess.refresh(request)
        self.assertEqual(
            request.request_status.request_status,
            RequestStatusEnum.declined.value,
        )

    def test_request_group_after_allocation(self):
        _ = self.allocation_manager.automatic_allocation(self.allocation_args)

        #   New request to a free resource
        request = self.request_manager.create_item(
            {
                "iteration_id": 1,
                "requested_date": dt.date(2020, 1, 2),
                "user_id": 1,
                "requested_resource_group_id": 4,
            },
        )

        self.assertIsNotNone(request.id)
        allocated_resource: list[AllocationModel] = [
            item
            for item
            in self.allocation_manager.list_all_items()
            if item.source_request_id == request.id
        ]
        self.assertEqual(len(allocated_resource), 1)
        self.assertEqual(allocated_resource[0].allocated_resource_id, 3)
        self.sess.refresh(request)
        self.assertEqual(
            request.request_status.request_status,
            RequestStatusEnum.completed.value,
        )

        #   New request to a busy resource - should get a different free resource in the same group
        request = self.request_manager.create_item(
            {
                "iteration_id": 1,
                "requested_date": dt.date(2020, 1, 2),
                "user_id": 2,
                "requested_resource_group_id": 4,
            },
        )
        allocated_resource: list[AllocationModel] = [
            item
            for item
            in self.allocation_manager.list_all_items()
            if item.source_request_id == request.id
        ]
        self.assertEqual(len(allocated_resource), 1)
        self.assertEqual(allocated_resource[0].allocated_resource_id, 4)
        self.sess.refresh(request)
        self.assertEqual(
            request.request_status.request_status,
            RequestStatusEnum.completed.value,
        )

        #   New request when no resources are free
        request = self.request_manager.create_item(
            {
                "iteration_id": 1,
                "requested_date": dt.date(2020, 1, 2),
                "user_id": 3,
                "requested_resource_group_id": 4,
            },
        )
        allocated_resource = [
            item
            for item
            in self.allocation_manager.list_all_items()
            if item.source_request_id == request.id
        ]
        self.assertEqual(len(allocated_resource), 0)
        self.sess.refresh(request)
        self.assertEqual(
            request.request_status.request_status,
            RequestStatusEnum.declined.value,
        )

    def test_delete_or_modify_request_after_allocation(self):
        _ = self.allocation_manager.automatic_allocation(self.allocation_args)

        #   Modify item - should delete the allocation and create a new one
        request = self.requests[0]
        old_allocation = request.allocation
        request = self.request_manager.modify_item(request.id, {"requested_resource_id": 2})
        new_allocation = request.allocation
        self.assertIsNone(self.allocation_manager.list_single_item(old_allocation.id))
        self.assertIsNotNone(new_allocation)

        #   Delete the item - should delete the allocation without creating a new one, reuse the
        #   modified request
        _ = self.request_manager.delete_item(request.id)
        request = self.request_manager.list_single_item(request.id)
        self.assertIsNone(request)
        new_allocation = self.allocation_manager.list_single_item(new_allocation.id)
        self.assertIsNone(new_allocation)
