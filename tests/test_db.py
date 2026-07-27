"""
Test for the db module
"""

import unittest
from unittest.mock import MagicMock, patch

from resource_allocator.config import Config
from resource_allocator.db import get_session


@patch("resource_allocator.db.Config", spec=Config)
class GetSessionTestCase(unittest.TestCase):
    def test_get_session(self, config: MagicMock):
        _ = get_session()
        config.get_session.assert_called()
