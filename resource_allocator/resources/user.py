"""
Resources related to working with users
"""

from flask import request, abort, Flask, Blueprint

from resource_allocator.config import Config
from resource_allocator.managers.user import (
    AuthManager,
    UserManager,
)
from resource_allocator.resources.base import BaseResource, CRUDResource, auth
from resource_allocator.schemas.user import (
    RegisterUserRequestSchema,
    LoginUserRequestSchema,
    LoginUserResponseSchema,
    LoginUserAzureRequestSchema,
    UserRequestSchema,
    UserResponseSchema,
)
from resource_allocator.utils.schema import validate_schema


class UserResource(CRUDResource):
    manager_class = UserManager
    request_schema = UserRequestSchema
    response_schema = UserResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["admin"]

    @auth.login_required
    def post(self) -> None:
        abort(400, "Users cannot be created. Use the register endpoint")

    @auth.login_required
    def get(self, id: int | None = None) -> dict | list:
        if request.path.endswith("me"):
            id = auth.current_user().id

        return super().get(id)

    @classmethod
    def register_method_view(
        cls,
        app: Flask | Blueprint,
        name: str,
        config: Config,
        rule: str | None = None,
    ) -> None:
        """
        Register a CRUD resource and add an additional /users/me endpoint"
        """
        super().register_method_view(app, name, config=config)
        app.add_url_rule(
            f"/{name}/me",
            view_func=cls.as_view(
                name=f"{name}-me",
                config=config,
            ),
        )


class RegisterUserResource(BaseResource):
    """
    API endpoint for registering users

    Methods:
        post: post request to register
    """
    manager_class = AuthManager
    request_schema = RegisterUserRequestSchema
    response_schema = LoginUserResponseSchema

    @validate_schema(RegisterUserRequestSchema)
    def post(self) -> dict:
        """
        Validate registration fields and write a user to the database

        Args:
            None

        Returns:
            dict: dictionary with a Bearer token
        """
        data = request.get_json()
        result = self.manager.register(data)

        #   In case manager returns ("message", error_code)
        if len(result) > 1:
            return result

        return self.response_schema().dump(result)


class LoginUserResource(BaseResource):
    """
    API endpoint for logging in a user

    Methods:
        post: post request to log in a user
    """
    manager_class = AuthManager
    request_schema = LoginUserRequestSchema
    response_schema = LoginUserResponseSchema

    @validate_schema(LoginUserRequestSchema)
    def post(self) -> dict:
        """
        Validate log-in fields, validate a user's password and return a token

        Args:
            None

        Returns:
            dict: dictionary with a Bearer token
        """
        data = request.get_json()
        result = self.manager.login(data)

        #   In case manager returns ("message", error_code)
        if len(result) > 1:
            return result

        return self.response_schema().dump(result)


class LoginUserAzureResource(BaseResource):
    """
    API Endpoint for logging in and implicitly registering external users via Azure Active Directory

    Methods:
        get: get request that returns an authentication URL that users must visit
        post: finish the Azure log-in process by consuming an authorization code
    """
    manager_class = AuthManager
    request_schema = RegisterUserRequestSchema
    response_schema = LoginUserResponseSchema

    def get(self) -> dict:
        return self.manager.login_azure_init(data=request.args)

    @validate_schema(LoginUserAzureRequestSchema)
    def post(self) -> dict:
        data = request.get_json()
        result = self.manager.login_azure_finish(data)

        #   In case manager returns ("message", error_code)
        if len(result) > 1:
            return result

        return self.response_schema().dump(result)
