"""
Utitlity functions and/or classes related to user authentication
"""

import datetime as dt
from typing import Optional

import jwt

def generate_token(id: int, secret: str, now: Optional[dt.datetime] = None) -> str:
    """
    Generate a JWT token for the specified user id

    Args:
        id: identifier to encode as a subject (sub)
        secret: secret to use as an encryption key
        now: what point in time to use as the current timestamp; use the current UTC timestamp if
            None [default: None]
    Returns:
        str: encoded token
    """
    now = now or dt.datetime.utcnow()
    data = {
        "sub": id,
        "iat": now,
        "exp": now + dt.timedelta(seconds = 3600),
    }
    return jwt.encode(data, key = secret, algorithm = "HS256")


def parse_token(token: str, secret: str) -> dict:
    """
    Parse a JWT token using a provided secret. Error handling should be handled upstream

    Args:
        token: string representing the JWT token
        secret: what secret to use as an encryption key

    Returns:
        dict: dictionary of the token payload
    """
    parsed_token = jwt.decode(token, key = secret, algorithms = ["HS256"])
    return parsed_token

