"""
User-related request schemas
"""

import re

from marshmallow import Schema, fields, validates, ValidationError

from resource_allocator.db import get_session
from resource_allocator.models import UserModel
from resource_allocator.schemas.base import BaseSchema


class RegisterUserRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)

    @validates("email")
    def validate_email(self, value):
        sess = get_session()
        emails = sess.query(UserModel.email).all()
        if (value, ) in emails:
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


class LoginUserRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class LoginUserResponseSchema(Schema):
    id = fields.Integer()
    token = fields.String()


class LoginUserAzureRequestSchema(Schema):
    email = fields.Email(required=True)
    code = fields.String(required=True)
    redirect_uri = fields.String()


class UserRequestSchema(BaseSchema):
    pass


class UserResponseSchema(BaseSchema):
    email = fields.Email()
    first_name = fields.String()
    last_name = fields.String()
    role_id = fields.Integer()
    role = fields.Dict()
    is_external = fields.Boolean()
