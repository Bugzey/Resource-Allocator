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
from resource_allocator.managers.user import UserManager
from resource_allocator.models import (
    metadata, populate_enums, AllocationModel, IterationModel, RequestStatusEnum
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
        self.users = [
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
        [UserManager.register(user) for user in self.users]

        self.resource_groups = [
            {
                "name": "top-level",
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
        ]
        [ResourceGroupManager.create_item(item) for item in self.resource_groups]

        self.resources = [
            {
                "name": "desk1",
                "top_resource_group_id": 1,
            },
            {
                "name": "desk2",
                "top_resource_group_id": 1,
            },
        ]
        [ResourceManager.create_item(item) for item in self.resources]

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

        self.iteration = {
            "start_date": dt.date(2020, 1, 1), "end_date": dt.date(2020, 1, 7),
        }
        IterationManager.create_item(self.iteration)

        self.requests = [
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
            },  # to be declined?
        ]
        [RequestManager.create_item(item) for item in self.requests]

        self.allocation_args = {
            "iteration_id": 1,
        }

    def tearDown(self):
        self.sess.rollback()
        metadata.drop_all(bind=self.engine)

    def test_automatic_allocation(self):
        result = AllocationManager.automatic_allocation(self.allocation_args)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 2)  # 2 days

        #   Result is written to the database
        self.assertEqual(self.sess.query(AllocationModel).all(), result)

        #   Iteration is now closed for requests
        self.assertFalse(self.sess.get(IterationModel, 1).accepts_requests)

        #   Request statuses
        requests = RequestManager.list_all_items()
        self.assertEqual(
            requests[0].request_status.request_status,
            RequestStatusEnum.completed.value,
        )
        self.assertEqual(
            requests[1].request_status.request_status,
            RequestStatusEnum.completed.value,
        )
        self.assertEqual(
            requests[-1].request_status.request_status,
            RequestStatusEnum.declined.value,
        )
