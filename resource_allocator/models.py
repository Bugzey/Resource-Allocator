"""
Database models creation
"""

from enum import Enum
import sqlalchemy as db
from sqlalchemy import orm
from sqlalchemy.orm import(
    declarative_base,
)

from resource_allocator.db import engine, sess

metadata = db.MetaData(bind = engine, schema = "resource_allocator")

class BaseBase:
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    created_date = db.Column(
        db.DateTime, server_default = db.func.now(), nullable = False,
    )
    updated_time = db.Column(
        db.DateTime,
        server_default = db.func.now(),
        nullable = False,
        onupdate = db.func.now(),
    )

Base = declarative_base(cls = BaseBase, metadata = metadata)


class RoleEnum(Enum):
    user = "user"
    admin = "admin"


class RoleModel(Base):
    __tablename__ = "role"
    role = db.Column(db.String(255), nullable = False)


class UserModel(Base):
    __tablename__ = "user"
    email = db.Column(db.String(255), nullable = False)
    password_hash = db.Column(db.String(255), nullable = False)
    role_id = db.Column(db.Integer, nullable = False)
    role = orm.relationship("RoleModel")


class IterationModel(Base):
    __tablename__ = "iteration"
    pass


class RequestModel(Base):
    __tablename__ = "request"
    pass


class ResourceModel(Base):
    __tablename__ = "resource"
    pass


class ResourceGroupModel(Base):
    __tablename__ = "resource_group"
    pass


class Allocation(Base):
    __tablename__ = "allocation"
    pass

