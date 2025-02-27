"""
Unit tests for utils.auth
"""

import datetime as dt
import unittest

import requests as req

from resource_allocator.utils import auth


class GenerateTokenTestCase(unittest.TestCase):
    def setUp(self):
        self.secret = "some_secret"
        self.id = 12

    def test_generate_token(self):
        token = auth.generate_token(id=self.id, secret=self.secret)
        self.assertTrue(isinstance(token, str))
        self.assertGreater(len(token), 0)


class ValidateTokenTestCase(unittest.TestCase):
    def setUp(self):
        self.secret = "some_secret"
        self.id = 12

    def test_validate_token(self):
        #   NOTE: this depends on utils.auth.generate_token
        token = auth.generate_token(id=self.id, secret=self.secret)
        parsed_token = auth.parse_token(token, secret=self.secret)
        self.assertLessEqual(set(["iat", "exp", "sub"]), set(parsed_token.keys()))
        self.assertEqual(parsed_token["sub"], str(self.id))

    def test_expired_token(self):
        token = auth.generate_token(
            id=self.id,
            secret=self.secret,
            now=dt.datetime(2000, 1, 1),
        )

        with self.assertRaises(auth.jwt.ExpiredSignatureError):
            _ = auth.parse_token(token=token, secret=self.secret)


class AzureConfiguredTestCase(unittest.TestCase):
    def test_azure_configured_true(self):
        @auth.azure_configured(lambda: True)
        def some_fun(arg): return arg

        result = some_fun("bla")
        self.assertEqual(result, "bla")

    def test_azure_configured_false(self):
        @auth.azure_configured(lambda: False)
        def some_fun(arg): return arg

        result = some_fun("bla")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1], 400)
        self.assertIn("not configured", result[0])


class BuildAzureADAuthUrlTestCase(unittest.TestCase):
    tenant_id = "tenant_id"
    aad_client_id = "aad_client_id"
    aad_client_secret = "aad_client_secret"
    redirect_uri = "redirect_uri"
    scopes = ["bla", "bla2"]

    def test_build_azure_ad_auth_url_no_scopes(self):
        result = auth.build_azure_ad_auth_url(
            tenant_id=self.tenant_id,
            aad_client_id=self.aad_client_id,
            redirect_uri=self.redirect_uri,
            scopes=None,
        )
        self.assertTrue(isinstance(result, str))
        self.assertIn(self.tenant_id, result)
        self.assertIn(self.aad_client_id, result)
        self.assertIn(self.redirect_uri, result)
        self.assertIn("User.ReadBasic.All", result)
        self.assertNotIn(self.aad_client_secret, result)

    def test_build_azure_ad_auth_url_with_scopes(self):
        result = auth.build_azure_ad_auth_url(
            tenant_id=self.tenant_id,
            aad_client_id=self.aad_client_id,
            redirect_uri=self.redirect_uri,
            scopes=self.scopes,
        )
        self.assertIn(self.scopes[0], result)
        self.assertIn(self.scopes[1], result)
        self.assertNotIn("User.ReadBasic.All", result)


class BuildAzureADTokenRequest(unittest.TestCase):
    tenant_id = "tenant_id"
    aad_client_id = "aad_client_id"
    aad_client_secret = "aad_client_secret"
    redirect_uri = "redirect_uri"
    scopes = ["bla", "bla2"]

    def test_build_azure_ad_token_request_no_scopes(self):
        result = auth.build_azure_ad_token_request(
            code="some_code",
            tenant_id=self.tenant_id,
            aad_client_id=self.aad_client_id,
            aad_client_secret=self.aad_client_secret,
            redirect_uri=self.redirect_uri,
            scopes=None,
        )
        self.assertTrue(isinstance(result, req.Request))
        self.assertIn(self.tenant_id, result.url)
        self.assertIn("token", result.url)
        self.assertEqual(result.data["code"], "some_code")
