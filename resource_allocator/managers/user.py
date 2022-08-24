"""
Logic manager for user-related options
"""

from collections.abc import Callable
from functools import wraps

from flask import request
from flask_httpauth import HTTPTokenAuth
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from resource_allocator.db import sess
from resource_allocator.models import UserModel, RoleModel
from resource_allocator.utils.auth import generate_token, parse_token
from resource_allocator.config import SECRET

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

        return {"token": generate_token(user.id, secret = SECRET)}


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

