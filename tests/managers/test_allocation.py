"""
Unit tests for managers.allocation
"""

import datetime as dt
import unittest

from resource_allocator.config import Config
from resource_allocator.db import get_session
from resource_allocator.managers.allocation import AllocationManager
from resource_allocator.managers.iteration import IterationManager
from resource_allocator.managers.request import RequestManager
from resource_allocator.managers.resource import ResourceManager, ResourceGroupManager
from resource_allocator.managers.resource_to_group import ResourceToGroupManager
from resource_allocator.managers.user import AuthManager, UserManager
from resource_allocator.models import (
    metadata, populate_enums, AllocationModel, IterationModel, RequestStatusEnum, RequestModel,
)
from resource_allocator.utils.db import change_schema

metadata = change_schema(metadata, schema="resource_allocator_test")


class AllocationManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Config.from_environment()
        self.sess = get_session()
        self.engine = self.sess.bind

        metadata.drop_all(self.engine)  # in case of errors during setUp
        metadata.create_all(self.engine)
        populate_enums(self.sess)
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
        _ = [AuthManager.register(user) for user in self.users_data]
        self.users = UserManager.list_all_items()

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
        self.resource_groups = [
            ResourceGroupManager.create_item(item)
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
        self.resources = [ResourceManager.create_item(item) for item in self.resources_data]

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
        [ResourceToGroupManager.create_item(item) for item in self.resource_to_group]

        self.iteration = IterationManager.create_item({
            "start_date": dt.date(2020, 1, 1), "end_date": dt.date(2020, 1, 7),
        })

        self.requests_data = [
            {
                "iteration_id": 1,
                "requested_date": dt.date(2020, 1, 1),
                "user_id": 1,
                "requested_resource_id": 1,
            },
            {
                "iteration_id": 1,
                "requested_date": dt.date(2020, 1, 1),
                "user_id": 2,
                "requested_resource_group_id": 3,
            },
            {
                "iteration_id": 1,
                "requested_date": dt.date(2020, 1, 1),
                "user_id": 3,
                "requested_resource_group_id": 3,
            },  # Declined since no more resources are available
            {
                "iteration_id": 1,
                "requested_date": dt.date(2020, 1, 1),
                "user_id": 1,
                "requested_resource_group_id": 4,
            },  # User 1 requests a resource in a different top resource group id
        ]
        self.requests = [RequestManager.create_item(item) for item in self.requests_data]

        self.allocation_args = {
            "iteration_id": 1,
        }

    def tearDown(self):
        self.sess.flush()
        self.sess.rollback()
        metadata.drop_all(bind=self.engine)

    def test_create_item(self):
        result = AllocationManager.create_item(data=dict(
            iteration_id=self.iteration.id,
            date=dt.date(2020, 1, 1),
            user_id=self.users[0].id,
            allocated_resource_id=self.resources[0].id,
            source_request_id=self.requests[0].id,
        ))
        self.assertIsInstance(result, AllocationModel)

        #   Check that the source request is completed
        request: RequestModel = self.requests[0]
        self.assertEqual(request.request_status.request_status, RequestStatusEnum.completed.value)

    def test_delete_item(self):
        result = AllocationManager.create_item(data=dict(
            iteration_id=self.iteration.id,
            date=dt.date(2020, 1, 1),
            user_id=self.users[0].id,
            allocated_resource_id=self.resources[0].id,
            source_request_id=self.requests[0].id,
        ))
        self.assertIsInstance(result, AllocationModel)

        #   Delete the allocation
        AllocationManager.delete_item(result.id)

        #   Check that the source request is completed
        request: RequestModel = self.requests[0]
        self.assertEqual(request.request_status.request_status, RequestStatusEnum.declined.value)

    def test_automatic_allocation(self):
        result = AllocationManager.automatic_allocation(self.allocation_args)
        self.assertTrue(isinstance(result, list))

        #   Result is written to the database
        self.assertEqual(self.sess.query(AllocationModel).all(), result)

        #   Iteration is now closed for requests
        self.assertTrue(self.sess.get(IterationModel, 1).is_allocated)

        #   Request statuses
        requests = RequestManager.list_all_items()
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
        new = AllocationManager.automatic_allocation(self.allocation_args)
        self.assertTrue(isinstance(new, list))
        self.assertEqual(len(new), 0)
        self.assertEqual(len(AllocationManager.list_all_items()), len(result))

    def test_request_resource_after_allocation(self):
        _ = AllocationManager.automatic_allocation(self.allocation_args)

        #   New request to a free resource
        request = RequestManager.create_item(
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
        request = RequestManager.create_item(
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
        request = RequestManager.create_item(
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
        _ = AllocationManager.automatic_allocation(self.allocation_args)

        #   New request to a free resource
        request = RequestManager.create_item(
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
            in AllocationManager.list_all_items()
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
        request = RequestManager.create_item(
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
            in AllocationManager.list_all_items()
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
        request = RequestManager.create_item(
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
            in AllocationManager.list_all_items()
            if item.source_request_id == request.id
        ]
        self.assertEqual(len(allocated_resource), 0)
        self.sess.refresh(request)
        self.assertEqual(
            request.request_status.request_status,
            RequestStatusEnum.declined.value,
        )

    def test_delete_or_modify_request_after_allocation(self):
        _ = AllocationManager.automatic_allocation(self.allocation_args)

        #   Modify item - should delete the allocation and create a new one
        request = self.requests[0]
        old_allocation = request.allocation
        request = RequestManager.modify_item(request.id, {"requested_resource_id": 2})
        new_allocation = request.allocation
        self.assertIsNone(AllocationManager.list_single_item(old_allocation.id))
        self.assertIsNotNone(new_allocation)

        #   Delete the item - should delete the allocation without creating a new one, reuse the
        #   modified request
        _ = RequestManager.delete_item(request.id)
        request = RequestManager.list_single_item(request.id)
        self.assertIsNone(request)
        new_allocation = AllocationManager.list_single_item(new_allocation.id)
        self.assertIsNone(new_allocation)
