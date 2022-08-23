"""
Database configuration module
"""

import sqlalchemy as db
from sqlalchemy.orm import Session

from resource_allocator.config import URL
import resource_allocator.models as models

engine = db.create_engine(URL)
models.metadata.bind = engine
sess = db.orm.Session(bind = engine)

