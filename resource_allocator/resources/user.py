"""
Resources related to working with users
"""

from flask import request
from flask_restful import Resource

from resource_allocator.managers.user import UserManager
from resource_allocator.schemas.request.user import (
    RegisterUserRequestSchema, LoginUserRequestSchema,
)
from resource_allocator.utils.schema import validate_schema


class RegisterUser(Resource):
    """
    API endpoint for registering users

    Methods:
        do_post: post request to register
    """
    @validate_schema(RegisterUserRequestSchema)
    def do_post(self) -> dict:
        """
        Validate registration fields and write a user to the database

        Args:
            None

        Returns:
            dict: dictionary with a Bearer token
        """
        data = request.get_json()
        token = UserManager.register(request.data)
        return token


class LoginUser(Resource):
    """
    API endpoint for logging in a user

    Methods:
        do_post: post request to log in a user
    """
    @validate_schema(LoginUserRequestSchema)
    def do_post(self) -> dict:
        """
        Validate log-in fields, validate a user's password and return a token

        Args:
            None

        Returns:
            dict: dictionary with a Bearer token
        """
        data = request.get_json()
        token = UserManager.login(data)
        return token

