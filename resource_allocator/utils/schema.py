"""
Schema-related utility functions
"""

from collections.abc import Callable
from functools import wraps
from typing import ClassVar

from flask import request
import marshmallow

def validate_schema(schema_name: ClassVar[marshmallow.Schema]) -> Callable:
    """
    Decorator for validating input schemas given a schema class

    Args:
        schema_name: class of the schema to validate

    Returns:
        Callable: decorator function
    """
    def wrapper(fun):
        @wraps(fun)
        def wrapped(*args, **kwargs):
            schema = schema_name()
            errors = schema.validate(request.get_json())
            if errors:
                return "Data validation errors: {}".format(errors), 400

            return fun(*args, **kwargs)
        return wrapped
    return wrapper

