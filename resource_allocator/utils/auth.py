"""
Utitlity functions and/or classes related to user authentication
"""

import datetime as dt
from functools import wraps
from typing import Optional

import requests as req
import jwt


def generate_token(id: int, secret: str, now: Optional[dt.datetime] = None) -> str:
    """
    Generate a JWT token for the specified user id

    Args:
        id: identifier to encode as a subject (sub)
        secret: secret to use as an encryption key
        now: what point in time to use as the current timestamp; use the current UTC timestamp if
            None [default: None]
    Returns:
        str: encoded token
    """
    now = now or dt.datetime.utcnow()
    data = {
        "sub": id,
        "iat": now,
        "exp": now + dt.timedelta(seconds = 3600),
    }
    return jwt.encode(data, key = secret, algorithm = "HS256")


def parse_token(token: str, secret: str) -> dict:
    """
    Parse a JWT token using a provided secret. Error handling should be handled upstream

    Args:
        token: string representing the JWT token
        secret: what secret to use as an encryption key

    Returns:
        dict: dictionary of the token payload
    """
    parsed_token = jwt.decode(token, key = secret, algorithms = ["HS256"])
    return parsed_token


def azure_configured(ok: bool):
    """
    Wrapper to check if Azure integration is configured. Will raise an Exception if it is not.

    Args:
        azure_configured: bool: whether all variables are configured. The value of
            config.AZURE_CONFIGURED should be passed
    """
    def wrapper(fun):
        @wraps(fun)
        def wrapped(*args, **kwargs):
            if ok:
                return fun(*args, **kwargs)

            raise Exception(
                "Azure Active Directory integration is not configured. Contact your administrator "
                "for more info"
            )

        return wrapped
    return wrapper


def build_azure_ad_auth_url(
    tenant_id: str, aad_client_id: str, redirect_uri: str, scopes: list[str] | None = None
) -> str:
    """
    Create an authorization URL that a user must visit in order to authotize delegated access
    permissions

    Args:
        tenant_id: Azure tenant ID
        aad_client_id: Client (application) ID for an Azure Active Directory app registration
        redirect_uri: URI to redirect the user to after authorizing
        scopes: list[str]: optional list of custom scopes; if None: defaults to
            ["User.ReadBasic.All"]; default: None

    Returns:
        str: an authorization URL
    """
    scopes = scopes or ["User.ReadBasic.All"]
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
    params = {
        "response_type": "code",
        "client_id": aad_client_id,
        "redirect_uri": redirect_uri,
        "scope": scopes,
    }
    request = req.Request(
        method = "GET",
        url = url,
        params = params,
    )
    return request.prepare().url


def build_azure_ad_token_request(
    code: str,
    tenant_id: str,
    aad_client_id: str,
    aad_client_secret: str,
    redirect_uri: str,
    scopes: list[str] | None = None,
) -> req.Request:
    """
    Prepare a requests.Request for completing the Azure Active Directory Login procedure - provide
    an authorization token and exchange it for an access token

    Args:
        tenant_id: Azure tenant ID
        aad_client_id: Client (application) ID for an Azure Active Directory app registration
        aad_client_secret: Client (application) secret for an Azure Active Directory app registration
        redirect_uri: URI to redirect the user to after authorizing
        scopes: list[str]: optional list of custom scopes; if None: defaults to
            ["User.ReadBasic.All"]; default: None

    Returns:
        req.Request: a prepared req.Request object for asking for a token
    """
    scopes = scopes or ["User.ReadBasic.All"]
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    params = {
        "grant_type": "authorization_code",
        "client_id": aad_client_id,
        "client_secret": aad_client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
        "scope": scopes,
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    request = req.Request(
        method = "POST",
        url = url,
        headers = headers,
        data = params,
    )
    return request

