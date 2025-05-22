"""
Base resource for defining repeatable CRUD-like operations quicker
"""
from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable

from flask import request, abort
from flask_restful import Resource
from marshmallow import Schema

from resource_allocator.managers.user import auth, get_user_role
from resource_allocator.managers.base import BaseManager


class BaseResource(ABC, Resource):
    @property
    @abstractmethod
    def manager(self) -> BaseManager: ...

    @property
    @abstractmethod
    def request_schema(self) -> Schema: ...

    @property
    @abstractmethod
    def response_schema(self) -> Schema: ...

    @property
    @abstractmethod
    def read_roles_required(self) -> list[str]: ...

    @property
    @abstractmethod
    def write_roles_required(self) -> list[str]: ...

    @staticmethod
    def check_read(fun: Callable) -> Callable:
        @wraps(fun)
        def inner(self, *args, **kwargs):
            if not get_user_role() in self.read_roles_required:
                abort(403, "Forbidden")

            return fun(self, *args, **kwargs)

        return inner

    @staticmethod
    def check_write(fun: Callable) -> Callable:
        @wraps(fun)
        def inner(self, *args, **kwargs):
            if not get_user_role() in self.write_roles_required:
                abort(403, "Forbidden")

            return fun(self, *args, **kwargs)

        return inner

    @auth.login_required
    @check_read
    def get(self, id: int | None = None) -> dict | list:
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
        if id is None:
            result = self.manager.list_all_items()
            return self.response_schema().dump(result, many=True)

        result = self.manager.list_single_item(id)
        return self.response_schema().dump(result)

    @auth.login_required
    @check_write
    def post(self) -> dict:
        """
        Create an item using the provided fields in the request json

        Args:
            None

        Returns:
            dict: dictionary of the attributes of the created object
        """
        data = request.get_json()

        #   Can't validate the schema with a decorator while using a base resource
        errors = self.request_schema().validate(data)
        if errors:
            abort(400, f"Data validation errors: {errors}")

        result = self.manager.create_item(self.request_schema().load(data))
        return self.response_schema().dump(result)

    @auth.login_required
    @check_write
    def delete(self, id: int | None = None):
        """
        Issue a delete statement on a resource

        Args:
            id: numeric identifier

        Returns:
            Content of the deleted item
        """
        if id is None:
            abort(400, "Delete action requires an object ID")

        result = self.manager.delete_item(id)
        return self.response_schema().dump(result)

    @auth.login_required
    @check_write
    def put(self, id: int | None = None):
        if id is None:
            abort(400, "Put action requires an object ID")

        data = request.get_json()
        existing = self.request_schema().dump(self.manager.list_single_item(id))
        existing = {key: value for key, value in existing.items() if value is not None}
        combined = {**existing, **data}

        #   Can't validate the schema with a decorator while using a base resource
        errors = self.request_schema().validate(combined, partial=True)
        if errors:
            return abort(400, f"Data validation errors: {errors}")

        result = self.manager.modify_item(id, self.request_schema().load(combined))
        return self.response_schema().dump(result)
