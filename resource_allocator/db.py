"""
Database configuration module
"""

import sqlalchemy as db

from resource_allocator.config import Config


def get_session() -> db.orm.Session:
    """
    Thin wrapper of Config.get_session - creates a new session whenever called
    """
    sess = Config.get_session()

    #   Check if session requires a manual rollback
    try:
        sess.connection()
    except db.exc.PendingRollbackError:
        sess.rollback()

    return sess
