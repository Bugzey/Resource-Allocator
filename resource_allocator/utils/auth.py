"""
Utitlity functions and/or classes related to user authentication
"""

import datetime as dt
from functools import wraps
from typing import Optional, Callable

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
    now = now or dt.datetime.now(tz=dt.timezone.utc)
    data = {
        "sub": str(id),
        "iat": now,
        "exp": now + dt.timedelta(seconds=3600),
    }
    return jwt.encode(data, key=secret, algorithm="HS256")


def parse_token(token: str, secret: str) -> dict:
    """
    Parse a JWT token using a provided secret. Error handling should be handled upstream

    Args:
        token: string representing the JWT token
        secret: what secret to use as an encryption key

    Returns:
        dict: dictionary of the token payload
    """
    parsed_token = jwt.decode(token, key=secret, algorithms=["HS256"])
    return parsed_token


def check_configured(
    check_fun: Callable[[], bool],
    error_code: int = 400,
    error_message: str | None = None,
):
    """
    Generic decorator to check if a condition is fulfilled and optionally return a message when
    calling the function

    Args:
        ok: Callable: a function that takes no arguments and returns a boolean. If true - execute
            the function. Otherwise, return the error_code and an optional error_message
        error_code: int: what HTTP code to return when the ok is False [default: 400]
        error_message: str: message to return when ok is False [default: None]
    """
    def wrapper(fun):
        @wraps(fun)
        def wrapped(*args, **kwargs):
            if check_fun():
                return fun(*args, **kwargs)

            return error_message, error_code

        return wrapped
    return wrapper


def azure_configured(check_fun: Callable[[], bool]):
    """
    Wrapper to check if Azure integration is configured. Will raise an Exception if it is not.

    This wraps check_configured.

    Args:
        check_fun: Callable: a function that takes no argument and returns a boolean - whether all
            variables are configured.
    """
    return check_configured(
        check_fun,
        error_code=400,
        error_message=(
            "Azure Active Directory integration is not configured. Contact your "
            "administrator for more info."
        ),
    )


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
        method="GET",
        url=url,
        params=params,
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
        aad_client_secret: Client (application) secret for an Azure Active Directory app
            registration
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
        method="POST",
        url=url,
        headers=headers,
        data=params,
    )
    return request
