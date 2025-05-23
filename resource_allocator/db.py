"""
Database configuration module
"""

import sqlalchemy as db

from resource_allocator.config import Config
import resource_allocator.models as models


def get_session(echo: bool = False) -> db.orm.Session:
    """
    Create a session and inject it into an active Config object
    """
    config = Config.get_instance()
    if not config._sess:
        engine = db.create_engine(config.URL, echo=echo)
        models.metadata.bind = engine
        config._sess = db.orm.Session(bind=engine)

    #   Check if session requires a manual rollback
    try:
        _ = config._sess.connection()
    except db.exc.PendingRollbackError:
        config._sess.rollback()

    return config._sess
