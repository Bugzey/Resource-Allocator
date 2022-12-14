"""
Unit tests for managers.allocation
"""

import datetime as dt
import unittest
from unittest.mock import patch, MagicMock

from resource_allocator.db import sess, engine
from resource_allocator.managers.allocation import AllocationManager
from resource_allocator.managers.iteration import IterationManager
from resource_allocator.managers.request import RequestManager
from resource_allocator.managers.resource import ResourceManager, ResourceGroupManager
from resource_allocator.managers.resource_to_group import ResourceToGroupManager
from resource_allocator.managers.user import UserManager
from resource_allocator.models import (
    metadata, populate_enums, AllocationModel, IterationModel,
)
from resource_allocator.utils.db import change_schema

metadata = change_schema(metadata, schema = "resource_allocator_test")

class AllocationManagerTestCase(unittest.TestCase):
    def setUp(self):
        metadata.drop_all(engine) # in case of errors during setUp
        metadata.create_all(engine)
        populate_enums(metadata, sess)
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
        ]
        [RequestManager.create_item(item) for item in self.requests]

        self.allocation_args = {
            "iteration_id": 1,
        }

    def tearDown(self):
        sess.rollback()
        metadata.drop_all(bind = engine)

    def test_automatic_allocation(self):
        result = AllocationManager.automatic_allocation(self.allocation_args)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(len(result), 2) # 2 days

        #   Result is written to the database
        self.assertEqual(sess.query(AllocationModel).all(), result)

        #   Iteration is now closed for requests
        self.assertFalse(sess.get(IterationModel, 1).accepts_requests)

