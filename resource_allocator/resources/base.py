"""
Base resource for defining repeatable CRUD-like operations quicker
"""
from abc import ABC, abstractmethod
from typing import Optional, Union

from flask import request
from flask_restful import Resource
from marshmallow import Schema

from resource_allocator.managers.user import auth, role_required, get_user_role
from resource_allocator.managers.base import BaseManager


class BaseResource(ABC, Resource):
    @property
    @abstractmethod
    def manager(self) -> BaseManager:...

    @property
    @abstractmethod
    def request_schema(self) -> Schema:...

    @property
    @abstractmethod
    def response_schema(self) -> Schema:...

    @property
    @abstractmethod
    def read_role_required(self) -> str:...

    @property
    @abstractmethod
    def write_role_required(self) -> str:...

    @auth.login_required
    def get(self, id: Optional[int] = None) -> Union[dict, list]:
        """
        Get requrest to list a single object or multiple objects

        Args:
            id: identifier of the object to get; list all objects if None [default: None]

        Returns:
            dict: dictionary response if querying a single object or a list if querying
            multiple objects
        """
        #   Can't use decorators with arguments in base classes before the properties are redefined
        #   in child classes
        if not get_user_role() == self.read_role_required:
            return "Forbidden", 403

        if id is None:
            result = self.manager.list_all_items()
            return self.response_schema().dump(result, many = True)

        result = self.manager.list_single_item(id)
        return self.response_schema().dump(result)

    @auth.login_required
    def post(self) -> dict:
        """
        Create an item using the provided fields in the request json

        Args:
            None

        Returns:
            dict: dictionary of the attributes of the created object
        """
        #   Can't use decorators with arguments in base classes before the properties are redefined
        #   in child classes
        if not get_user_role() == self.write_role_required:
            return "Forbidden", 403

        data = request.get_json()

        #   Can't validate the schema with a decorator while using a base resource
        errors = self.request_schema().validate(data)
        if errors:
            return "Data validation errors: {}".format(errors), 400

        result = self.manager.create_item(self.request_schema().dump(data))
        return self.response_schema().dump(result)

