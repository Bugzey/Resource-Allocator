"""
Logic manager for user-related options
"""

from dataclasses import dataclass
import logging
from typing import Any

import requests as req
from werkzeug.security import generate_password_hash, check_password_hash

from resource_allocator.managers.base import BaseManager
from resource_allocator.models import UserModel, RoleModel, RoleEnum
from resource_allocator.utils.auth import (
    build_azure_ad_auth_url,
    build_azure_ad_token_request,
    generate_token,
)
from resource_allocator.config import Config


logger = logging.getLogger(__name__)


class UserManager(BaseManager):
    model = UserModel

    def modify_item(self, id: int, data: dict) -> UserModel:
        if "password" in data:
            data["password_hash"] = generate_password_hash(str(data["password"]))
            del data["password"]

        return super().modify_item(id, data)


@dataclass
class AuthManager(BaseManager):
    config: Config

    model = UserModel

    def register(self, data: dict) -> dict[str, str]:
        data = data.copy()
        data["password_hash"] = generate_password_hash(str(data["password"]))
        del data["password"]

        if self.sess.query(UserModel).first():
            role = RoleEnum.user.name
        else:
            role = RoleEnum.admin.name

        role_id = self.sess.query(RoleModel.id).where(RoleModel.role == role).scalar()
        data["role_id"] = role_id

        user = UserModel(**data)
        self.sess.add(user)
        self.sess.flush()

        return {"id": user.id, "token": generate_token(user.id, secret=self.config.SECRET)}

    def login(self, data: dict) -> dict[str, str]:
        user = self.sess.query(UserModel).where(UserModel.email == data["email"]).first()
        if not user:
            return "No such user: {}".format(data["email"]), 404

        if not check_password_hash(user.password_hash, str(data["password"])):
            return "Invalid password", 401

        return {"id": user.id, "token": generate_token(user.id, secret=self.config.SECRET)}

    def login_azure_init(self, data: dict | None = None) -> dict[str, str]:
        """
        Initiate or complete an Azure Active Directory login
        """
        data = data or {}
        config = self.config
        custom_redirect = data.get("redirect_uri")
        if (
            custom_redirect
            and not custom_redirect.startswith("http://localhost")
            and custom_redirect not in config.ALLOWED_ORIGINS
        ):
            return (
                (
                    f"Custom redirects can only be localhost or from allowed origins. "
                    f"Got {custom_redirect}"
                ),
                400
            )

        return {
            "auth_url": build_azure_ad_auth_url(
                tenant_id=config.TENANT_ID,
                aad_client_id=config.AAD_CLIENT_ID,
                redirect_uri=custom_redirect or config.REDIRECT_URI,
            )
        }

    def _register_azure(self, user_response: dict[str, Any]) -> dict[str, str]:
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

        if self.sess.query(UserModel).first():
            role = RoleEnum.user.name
        else:
            role = RoleEnum.admin.name

        role_id = self.sess.query(RoleModel.id).where(RoleModel.role == role).scalar()

        user = UserModel(
            email=user_response["mail"].lower(),  # can have capitals in Azure AD
            password_hash=None,
            first_name=user_response["givenName"],
            last_name=user_response["surname"],
            role_id=role_id,
            is_external=True,
        )
        self.sess.add(user)
        self.sess.flush()
        return user

    def login_azure_finish(self, data: dict) -> dict[str, str]:
        """
        Finish the Azure Active Directory login by consuming an authorization code in exchange for
        an access token. We do not store any tokens.

        Args:
            data: dict: API request json. Must contain the "code" key and value
        """
        config = self.config
        auth_request = build_azure_ad_token_request(
            code=data["code"],
            tenant_id=config.TENANT_ID,
            aad_client_id=config.AAD_CLIENT_ID,
            aad_client_secret=config.AAD_CLIENT_SECRET,
            redirect_uri=data.get("redirect_uri", config.REDIRECT_URI),
            scopes=None,  # might be integrated in the future
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

        user = self.sess \
            .query(UserModel) \
            .where(UserModel.email == user_response["mail"].casefold()) \
            .first()

        if not user:
            user = self._register_azure(user_response)

        if user.email != data["email"].lower():
            return "Requested email is not the same as Azure AD response email.", 400

        if not user.is_external:
            return "User is not external; use password login", 400

        return {"id": user.id, "token": generate_token(user.id, secret=self.config.SECRET)}


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
        url="https://graph.microsoft.com/v1.0/me",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {azure_token}"
        },
    )
    return user.json()
