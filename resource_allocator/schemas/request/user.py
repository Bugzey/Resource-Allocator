"""
User-related request schemas
"""

import re

from marshmallow import Schema, fields, validates, ValidationError

from resource_allocator.db import sess
from resource_allocator.models import UserModel

class RegisterUserRequestSchema(Schema):
    email = fields.Email(required = True)
    password = fields.String(required = True)

    @validates("email")
    def validate_email(self, value):
        emails = sess.query(UserModel.email).all()
        if value in emails:
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
    email = fields.Email(required = True)
    password = fields.String(required = True)

