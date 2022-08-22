"""
Database configuration module
"""

import sqlalchemy as db
from sqlalchemy.orm import Session

from resource_allocator.config import URL

engine = db.create_engine(URL)
sess = db.orm.Session(bind = engine)

