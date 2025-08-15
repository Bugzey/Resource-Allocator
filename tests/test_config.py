"""
Unit tests for the config module
"""

from dataclasses import fields
import os
import tempfile
import unittest
from unittest.mock import patch

from sqlalchemy.engine import url

from resource_allocator.config import Config


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.kwargs = {item.name: item.name for item in fields(Config) if item.init}
        self.kwargs["LOCAL_LOGIN_ENABLED"] = "yes"
        self.kwargs["DB_PORT"] = 12

    def tearDown(self):
        Config.reset_instance()

    def test_init_no_azure(self):
        self.kwargs.pop("AAD_CLIENT_ID")
        self.kwargs.pop("AAD_CLIENT_SECRET")
        self.kwargs.pop("TENANT_ID")
        self.kwargs.pop("REDIRECT_URI")

        config = Config(**self.kwargs)
        self.assertTrue(isinstance(config, Config))
        self.assertFalse(config.AZURE_CONFIGURED)
        self.assertTrue(config.LOCAL_LOGIN_ENABLED)

    def test_init_with_azure(self):
        self.kwargs.pop("LOCAL_LOGIN_ENABLED")
        config = Config(**self.kwargs)

        self.assertTrue(isinstance(config, Config))
        self.assertFalse(config.LOCAL_LOGIN_ENABLED)

        #   Check compounds
        self.assertTrue(config.AZURE_CONFIGURED)
        self.assertTrue(isinstance(config.URL, url.URL))

    @staticmethod
    def patch_environ(fun):
        def inner(self, *args, **kwargs):
            @patch.dict(os.environ, self.kwargs)
            def more_inner(self, *args, **kwargs):
                return fun(self, *args, **kwargs)

        return inner

    @patch_environ
    def test_from_environment(self):
        config = Config.from_environment()
        self.assertTrue(isinstance(config, Config))
        self.assertTrue(config.LOCAL_LOGIN_ENABLED)
        self.assertTrue(config.AZURE_CONFIGURED)

        #   Singleton test
        self.assertGreater(len(Config._instance), 0)
        new_config = Config.from_environment()
        self.assertTrue(config is new_config)

        #   Again
        newer_config = Config.get_instance()
        self.assertTrue(config is newer_config)

    def test_from_config(self):
        data = "\n".join(f"{key} = {value}" for key, value in self.kwargs.items())

        with tempfile.NamedTemporaryFile("r+", encoding="utf-8") as cur_file:
            cur_file.write(data)
            cur_file.seek(0)
            config = Config.from_config(cur_file.name)

        self.assertTrue(isinstance(config, Config))
        self.assertTrue(config.LOCAL_LOGIN_ENABLED)
        self.assertTrue(config.AZURE_CONFIGURED)
