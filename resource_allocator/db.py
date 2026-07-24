"""
Database configuration module
"""

import sqlalchemy as db

from resource_allocator.config import Config


def get_session() -> db.orm.Session:
    """
    Thin wrapper of Config.get_session - creates a new session if one does not exist, reuses an
    existing sesion otherwise
    """
    sess = Config.get_session()
    return sess
