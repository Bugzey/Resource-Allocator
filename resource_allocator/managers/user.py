"""
Logic manager for user-related options
"""

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


auth = HTTPTokenAuth()

@auth.verify_token
def verify_token(fun):
    def wrapped(*args, **kwargs):
        if "Authorization" not in request.headers:
            return "Unauthenticated", 401

        token = re.find("Bearer (.+)", request.headers["Authorization"])
        if not token:
            return "Unauthenticated", 401

        try:
            parsed_token = parse_token(token = token, secret = SECRET)
        except jwt.ExpiredSignatureError:
            return "Token expired", 401
        except jwt.InvalidSignatureError:
            return "Invalid token signature", 401
        except jwt.DecodeError:
            return "Misc token validation error", 401

        user = sess.get(User, parsed_token["sub"])
        return user

