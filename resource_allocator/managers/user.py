"""
Logic manager for user-related options
"""

from collections.abc import Callable
from functools import wraps
import logging
from typing import Any

from flask import request
from flask_httpauth import HTTPTokenAuth
import jwt
import requests as req
from werkzeug.security import generate_password_hash, check_password_hash

from resource_allocator.db import sess
from resource_allocator.models import UserModel, RoleModel
from resource_allocator.utils.auth import (
    generate_token, parse_token, build_azure_ad_auth_url, build_azure_ad_token_request,
    azure_configured,
)
from resource_allocator.config import (
    SECRET, AAD_CLIENT_ID, AAD_CLIENT_SECRET, TENANT_ID, SERVER_NAME, REDIRECT_URI, AZURE_CONFIGURED
)

logger = logging.getLogger(__name__)


class UserManager:
    @staticmethod
    def register(data: dict) -> dict[str, str]:
        data = data.copy()
        data["password_hash"] = generate_password_hash(str(data["password"]))
        del data["password"]

        role_id = sess.query(RoleModel.id).where(RoleModel.role == "user").scalar()
        data["role_id"] = role_id

        user = UserModel(**data)
        sess.add(user)
        sess.flush()

        return {"token": generate_token(user.id, secret = SECRET)}

    @staticmethod
    def login(data: dict) -> dict[str, str]:
        user = sess.query(UserModel).where(UserModel.email == data["email"]).first()
        if not user:
            return "No such user: {}".format(data["email"]), 404

        if not check_password_hash(user.password_hash, str(data["password"])):
            return "Invalid password", 401

        return {"id": user.id, "token": generate_token(user.id, secret = SECRET)}

    @staticmethod
    @azure_configured(AZURE_CONFIGURED)
    def login_azure_init() -> dict[str, str]:
        """
        Initiate or complete an Azure Active Directory login
        """
        return {"auth_url": build_azure_ad_auth_url(
            tenant_id = TENANT_ID, aad_client_id = AAD_CLIENT_ID, redirect_uri = REDIRECT_URI,
        )}

    @staticmethod
    @azure_configured(AZURE_CONFIGURED)
    def _register_azure(user_response: dict[str, Any]) -> dict[str, str]:
        """
        Register a new Azure Active Directory user using the user response from Azure. This method
        should remain private

        Args:
            user_response: req.Response object as returned by the /me Microsoft Graph endpoint. More
                info:
                https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0&tabs=http#response-2

        Returns:
            models.UserModel: registered user model
        """
        logger.info(
            f"User {user_response['mail']} requested login but is not registered. Will "
            f"register automatically"
        )

        role_id = sess.query(RoleModel.id).where(RoleModel.role == "user").scalar()

        user = UserModel(
            email = user_response["mail"].lower(),  # can have capitals in Azure AD
            password_hash = None,
            first_name = user_response["givenName"],
            last_name = user_response["surname"],
            role_id = role_id,
            is_external = True,
        )
        sess.add(user)
        sess.flush()
        return user

    @staticmethod
    @azure_configured(AZURE_CONFIGURED)
    def login_azure_finish(data: dict) -> dict[str, str]:
        """
        Finish the Azure Active Directory login by consuming an authorization code in exchange for
        an access token. We do not store any tokens.

        Args:
            data: dict: API request json. Must contain the "code" key and value
        """
        auth_request = build_azure_ad_token_request(
            code = data["code"],
            tenant_id = TENANT_ID,
            aad_client_id = AAD_CLIENT_ID,
            aad_client_secret = AAD_CLIENT_SECRET,
            redirect_uri = REDIRECT_URI,
            scopes = None,  # might be integrated in the future
        )
        with req.session() as req_sess:
            auth_response = req_sess.send(auth_request.prepare())
            auth_response_json = auth_response.json()
            if not auth_response.ok:
                raise RuntimeError(
                    f"Bad response returned when authenticating Azure Active Directory user: "
                    f"{auth_response_json}"
                )
            azure_token = auth_response_json["access_token"]
            user_response = get_azure_user_info(azure_token)

        user = sess.query(UserModel).where(UserModel.email == user_response["mail"]).first()

        if not user:
            user = UserManager._register_azure(user_response)

        if not user.is_external:
            return "User is not external; use password login", 400

        return {"id": user.id, "token": generate_token(user.id, secret = SECRET)}


auth = HTTPTokenAuth(scheme = "Bearer")

@auth.verify_token
def verify_token(token):
    """
    Verify the JWT token and return whatever flask_httpauth requires

    Success: user object
    No user: True
    Failed auth: False
    """
    try:
        parsed_token = parse_token(token = token, secret = SECRET)
    except Exception:
        return False

    user = sess.get(UserModel, parsed_token["sub"])
    if not user:
        return True

    return user


def get_user_role() -> str:
    """
    Function to get the current user's roles

    Args:
        None

    Returns:
        str: name of the assigned user role
    """
    role = sess.get(RoleModel, auth.current_user().role_id).role
    return role


def role_required(role_name: str) -> Callable:
    """
    Decorator to check if a user has the required role role_name for an action

    Args:
        role_name: str: name of the role to check for

    Returns:
        Callable: wrapper function
    """
    def wrapper(fun):
        @wraps(fun)
        def wrapped(*args, **kwargs):
            user = auth.current_user()
            required_role_id = sess \
                .query(RoleModel.id) \
                .where(RoleModel.role == role_name) \
                .scalar()

            if not user.role_id == required_role_id:
                return "Forbidden", 403

            return fun(*args, **kwargs)
        return wrapped
    return wrapper


def get_azure_user_info(azure_token: str) -> dict[str, Any]:
    """
    Get info on the current Azure Active Directory user from the Graph REST API

    Reference: https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0&tabs=http

    Args:
        azure_token: access_token from logging in

    Returns:
        dict: dictionary of basic user properties
    """
    user = req.get(
        url = "https://graph.microsoft.com/v1.0/me",
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {azure_token}"
        },
    )
    return user.json()

