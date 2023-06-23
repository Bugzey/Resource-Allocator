"""
Database configuration module
"""

import sqlalchemy as db

from resource_allocator.config import Config
import resource_allocator.models as models


def get_session() -> db.orm.Session:
    """
    Create a session and inject it into an active Config object
    """
    config = Config.get_instance()
    if not config._sess:
        engine = db.create_engine(config.URL)
        models.metadata.bind = engine
        config._sess = db.orm.Session(bind=engine)

    return config._sess
