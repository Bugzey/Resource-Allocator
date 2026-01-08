"""
User-related request schemas
"""

import re

from marshmallow import Schema, fields, validates, validates_schema, ValidationError
from sqlalchemy import select, func

from resource_allocator.db import get_session
from resource_allocator.models import UserModel, RoleModel, RoleEnum
from resource_allocator.schemas.base import BaseRequestSchema, BaseResponseSchema


class RegisterUserRequestSchema(BaseRequestSchema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)

    @validates("email")
    def validate_email(self, value):
        sess = get_session()
        exists = sess.execute(
            select(UserModel.email)
            .where(func.lower(UserModel.email) == value.lower())
        ).first()
        if exists:
            raise ValidationError(f"Email {value} already registered")

    @validates("password")
    def validate_password(self, value):
        ok = True
        ok = ok and len(value) >= 6
        ok = ok and re.search(r"[a-z]", value)
        ok = ok and re.search(r"[A-Z]", value)
        ok = ok and re.search(r"\d", value)
        ok = ok and re.search(r"\W", value)

        if not ok:
            raise ValidationError("Invalid password")


class LoginUserRequestSchema(BaseRequestSchema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class LoginUserResponseSchema(Schema):  # avoid default response fields - created, updated
    id = fields.Integer()
    token = fields.String()


class LoginUserAzureRequestSchema(BaseRequestSchema):
    email = fields.Email(required=True)
    code = fields.String(required=True)
    redirect_uri = fields.String()


class UserRequestSchema(BaseResponseSchema):
    email = fields.Email()
    password = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    role_id = fields.Integer()

    _user: UserModel = None

    def get_user(self, id: int) -> UserModel:
        """
        Cache the current user
        """
        if self._user is None or self._user.id != id:
            sess = get_session()
            self._user = sess.get(UserModel, id)

        return self._user

    @validates("role_id")
    def validate_role_id(self, value):
        sess = get_session()
        role = sess.execute(
            select(RoleModel)
            .where(RoleModel.id == value)
        ).first()
        if not role:
            raise ValidationError(f"Invalid role_id: {value}")

    @validates_schema()
    def validate_email(self, data, **kwargs):
        email = data.get("email")
        if not email:
            return

        sess = get_session()
        exists = sess.execute(
            select(UserModel.email)
            .where(
                UserModel.id != data["id"],
                func.lower(UserModel.email) == email.lower(),
            )
        ).first()
        if exists:
            raise ValidationError(f"Email already in use: {email}")

    @validates_schema
    def validate_last_admin(self, data, **kwargs):
        role_id = data.get("role_id")
        if role_id is None:
            return

        sess = get_session()
        user = self.get_user(data["id"])
        admin_role_id = sess.execute(
            select(RoleModel.id)
            .where(RoleModel.role == RoleEnum.admin.value)
        ).scalar()

        if user.role.id != admin_role_id:
            return

        admin_count = sess.execute(
            select(func.count())
            .select_from(UserModel)
            .where(UserModel.role_id == admin_role_id)
        ).scalar()
        if admin_count <= 1 and data["role_id"] != admin_role_id:
            raise ValidationError("Last admin account cannot be changed to a user account")

    @validates_schema
    def validate_external_role_only(self, data, **kwargs):
        user = self.get_user(data["id"])
        if not user.is_external:
            return

        allowed_keys = ("role_id", )
        if keys_not_allowed := [
            item
            for item
            in data.keys()
            if item not in allowed_keys
            and item != "id"
        ]:
            raise ValidationError(
                f"Fields cannot be modified for external users: {keys_not_allowed}. "
                f"Allowed fields: {allowed_keys}"
            )


class UserResponseSchema(BaseResponseSchema):
    email = fields.Email()
    first_name = fields.String()
    last_name = fields.String()
    role_id = fields.Integer()
    is_external = fields.Boolean()
