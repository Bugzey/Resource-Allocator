"""
Base resource for defining repeatable CRUD-like operations quicker
"""
from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable

from flask import request, abort
from werkzeug.datastructures import MultiDict
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

    @classmethod
    def _paginate(self, args: MultiDict) -> tuple[int, int, list[str]]:
        """
        Check if limit, offset and order by are valid
        """
        limit = args.get("limit", "200")
        offset = args.get("offset", "0")
        order_by = args.getlist("order_by")  # returns empty list if key is missing

        #   Errors
        errors = {}
        if not limit.isnumeric() or not int(limit) > 0 or int(limit) > 1000:
            errors["limit"] = "Limit must be numeric, positive and less than 1000"
        if not offset.isnumeric() or not int(offset) >= 0:
            errors["offset"] = "Offset must be numeric and non-negative"

        schema = self.response_schema()
        if missing := [
            item.replace("-", "")
            for item
            in order_by
            if item.replace("-", "") not in schema.fields
        ]:
            errors["order_by"] = f"Order by fields not found: {', '.join(missing)}"

        if errors:
            abort(400, errors)

        return int(limit), int(offset), order_by

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
        #   Return a single item
        if id is not None:
            result = self.manager.list_single_item(id)
            return self.response_schema().dump(result)

        #   Return a list with limit, offset and group by
        limit, offset, order_by = self._paginate(request.args)
        result = self.manager.list_all_items(limit=limit, offset=offset, order_by=order_by)
        return self.response_schema().dump(result, many=True)

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
        data["id"] = id

        #   Can't validate the schema with a decorator while using a base resource
        data = {
            **{
                key: value
                for key, value
                in self.request_schema().dump(self.manager.list_single_item(id)).items()
                if value is not None
            },
            **data,
        }
        errors = self.request_schema().validate(data, partial=True)
        if errors:
            return abort(400, f"Data validation errors: {errors}")

        result = self.manager.modify_item(id, self.request_schema().load(data, partial=True))
        return self.response_schema().dump(result)
