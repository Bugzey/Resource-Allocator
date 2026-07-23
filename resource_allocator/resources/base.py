"""
Base resource for defining repeatable CRUD-like operations quicker
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from collections.abc import Callable
from functools import wraps

from flask import request, abort, Flask, Blueprint
from flask.views import MethodView
from flask_httpauth import HTTPTokenAuth
from marshmallow import Schema
from sqlalchemy.orm import Session

from resource_allocator.db import get_session
from resource_allocator.config import Config
from resource_allocator.models import UserModel, RoleModel, RoleEnum
from resource_allocator.managers.base import BaseManager
from resource_allocator.utils.auth import parse_token


auth = HTTPTokenAuth(scheme="Bearer")


@auth.verify_token
def verify_token(token):
    """
    Verify the JWT token and return whatever flask_httpauth requires

    Success: user object
    No user: True
    Failed auth: False
    """
    config = Config.get_instance()
    try:
        parsed_token = parse_token(token=token, secret=config.SECRET)
    except Exception:
        return False

    user = get_session().get(UserModel, int(parsed_token["sub"]))
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
    role = get_session().get(RoleModel, auth.current_user().role_id).role
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
            required_role_id = get_session() \
                .query(RoleModel.id) \
                .where(RoleModel.role == role_name) \
                .scalar()

            if not user.role_id == required_role_id:
                return "Forbidden", 403

            return fun(*args, **kwargs)
        return wrapped
    return wrapper


@dataclass
class BaseResource(ABC, MethodView):
    sess: Session
    config: Config | None = None

    def __post_init__(self):
        #   Instantiate the manager
        self.manager = self.manager_class(self.sess, config=self.config)

    @property
    @abstractmethod
    def manager_class(self) -> BaseManager: ...

    @property
    def read_roles_required(self) -> list[str]:
        """
        List of roles needed to read data. If not overwritten, returns RoleEnum.user and .admin
        """
        return [RoleEnum.user, RoleEnum.admin]

    @property
    def write_roles_required(self) -> list[str]:
        """
        List of roles needed to write data. If not overwritten, returns .admin
        """
        return [RoleEnum.admin]

    @property
    def request_schema(self) -> Schema:
        """
        Schema to validate a request. If not overwritten, then this returns a blank schema
        """
        return Schema

    @property
    @abstractmethod
    def response_schema(self) -> Schema:
        """
        Schema to validate and dump a response. If not overwritten, returns a blank schema
        """
        return Schema

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
    def register_view(
        cls,
        app: Flask | Blueprint,
        config: Config,
        name: str,
        rule: str | None = None,
    ) -> None:
        """
        Register the method view resource to an app or blueprint - register as a single endpoint

        Args:
            app: Flask app or Blueprint
            name: name of the endpoint
            config: Config instance if used by the manager_class
            rule: Optional specific URL rule in the form of /some/api/link - trailing slashes and
                arguments at the user's discretion. If None, register as "/name"
        """
        app.add_url_rule(
            rule=rule or f"/{name}",
            view_func=cls.as_view(
                name=name,
                sess=config.get_session(),
                config=config,
            ),
        )


class CRUDResource(BaseResource):
    @auth.login_required
    @BaseResource.check_read
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
    @BaseResource.check_write
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
    @BaseResource.check_write
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
    @BaseResource.check_write
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

    @classmethod
    def register_view(
        cls,
        app: Flask | Blueprint,
        config: Config,
        name: str,
        rule: str | None = None,
    ) -> None:
        """
        Register the method view resource to an app or blueprint

        This registration is specific to CRUD-resources - registering a {name}-group and a
        {name}-item URL rule handing /{name}/ and /{name}/<int:id> endpoint

        Args:
            app: Flask app or Blueprint
            config: optional Config instance if used by the manager_class
            name: name of the endpoint
            rule: optional rule notation. If blank, makes /{name}/ and /{name}/<int:id>
        """
        if rule:
            raise ValueError(
                f"CRUD Resources do not support a rule input - {rule}. Redefine the "
                "register_method_view method in stead"
            )

        app.add_url_rule(
            f"/{name}/",
            view_func=cls.as_view(
                name=f"{name}-group",
                sess=config.get_session(),
                config=config,
            ),
        )
        app.add_url_rule(
            f"/{name}/<int:id>",
            view_func=cls.as_view(
                name=f"{name}-item",
                sess=config.get_session(),
                config=config,
            ),
        )
