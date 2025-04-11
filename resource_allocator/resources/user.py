"""
Resources related to working with users
"""

from flask import request, abort
from flask_restful import Resource

from resource_allocator.managers.user import UserManager, auth
from resource_allocator.resources.base import BaseResource
from resource_allocator.schemas.user import (
    RegisterUserRequestSchema,
    LoginUserRequestSchema,
    LoginUserResponseSchema,
    LoginUserAzureRequestSchema,
    UserRequestSchema,
    UserResponseSchema,
)
from resource_allocator.utils.schema import validate_schema


class UserResource(BaseResource):
    manager = UserManager
    request_schema = UserRequestSchema
    response_schema = UserResponseSchema
    read_roles_required = ["user", "admin"]
    write_roles_required = ["admin"]

    @auth.login_required
    def post(self) -> None:
        abort(400, "Users cannot be created. Use the register endpoint")

    @auth.login_required
    def put(self, id: int):
        abort(400, "Users cannot be modified at this time")

    @auth.login_required
    def get(self, id: int | None = None) -> dict | list:
        if request.path.endswith("me"):
            id = auth.current_user().id

        return super().get(id)


class RegisterUser(Resource):
    """
    API endpoint for registering users

    Methods:
        post: post request to register
    """
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
        result = UserManager.register(data)

        #   In case manager returns ("message", error_code)
        if len(result) > 1:
            return result

        return LoginUserResponseSchema().dump(result)


class LoginUser(Resource):
    """
    API endpoint for logging in a user

    Methods:
        post: post request to log in a user
    """
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
        result = UserManager.login(data)

        #   In case manager returns ("message", error_code)
        if len(result) > 1:
            return result

        return LoginUserResponseSchema().dump(result)


class LoginUserAzure(Resource):
    """
    API Endpoint for logging in and implicitly registering external users via Azure Active Directory

    Methods:
        get: get request that returns an authentication URL that users must visit
        post: finish the Azure log-in process by consuming an authorization code
    """
    def get(self) -> dict:
        return UserManager.login_azure_init(data=request.args)

    @validate_schema(LoginUserAzureRequestSchema)
    def post(self) -> dict:
        data = request.get_json()
        result = UserManager.login_azure_finish(data)

        #   In case manager returns ("message", error_code)
        if len(result) > 1:
            return result

        return LoginUserResponseSchema().dump(result)
