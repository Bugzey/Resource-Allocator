"""
Database models creation
"""

from enum import Enum
import sqlalchemy as db
from sqlalchemy import (
    Column, String, Integer, Date, DateTime, ForeignKey, func, Boolean,
)
from sqlalchemy import orm
from sqlalchemy.orm import(
    declarative_base,
    relationship,
)

metadata = db.MetaData(schema = "resource_allocator")

class BaseBase:
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    created_time = db.Column(
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
    role = db.Column(db.String(255), nullable = False, unique = True)


class UserModel(Base):
    __tablename__ = "user"
    email = db.Column(db.String(255), nullable = False, unique = True)
    password_hash = db.Column(db.String(255), nullable = True)
    first_name = db.Column(db.String(255), nullable = False)
    last_name = db.Column(db.String(255), nullable = False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable = False)
    is_external = db.Column(db.Boolean, nullable = False, server_default = "false")
    role = orm.relationship("RoleModel")
    __table_args__ = (
        db.CheckConstraint(
            "password_hash is not NULL or is_external is TRUE",
            name = "check_internal_or_external"
        ),
    )


class ResourceGroupModel(Base):
    __tablename__ = "resource_group"
    name = Column(String(255), nullable = False, unique = True)
    is_top_level = Column(Boolean, nullable = False, server_default = "false")
    top_resource_group_id = Column(Integer(), ForeignKey("resource_group.id"))


class ResourceToGroupModel(Base):
    __tablename__ = "resource_to_group"
    resource_id = Column(Integer, ForeignKey("resource.id"), nullable = False)
    resource_group_id = Column(
        Integer,
        ForeignKey("resource_group.id"),
        nullable = False,
    )


class ResourceModel(Base):
    __tablename__ = "resource"
    name = Column(String(255), nullable = False, unique = True)
    top_resource_group_id = Column(Integer(), ForeignKey("resource_group.id"))
    resource_groups = relationship(
        "ResourceGroupModel",
        secondary = ResourceToGroupModel.__table__,
    )


class IterationModel(Base):
    __tablename__ = "iteration"
    start_date= Column(Date, nullable = False)
    end_date = Column(Date, nullable = False)
    accepts_requests = Column(Boolean, nullable = False, server_default = "true")
    requests = relationship("RequestModel")


class RequestModel(Base):
    __tablename__ = "request"
    iteration_id = Column(Integer, ForeignKey("iteration.id"), nullable = False)
    requested_date = Column(Date, nullable = False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable = False)
    requested_resource_id = Column(Integer, ForeignKey("resource.id"))
    requested_resource = relationship("ResourceModel")
    requested_resource_group_id = Column(Integer, ForeignKey("resource_group.id"))


class AllocationModel(Base):
    __tablename__ = "allocation"
    iteration_id = Column(Integer, ForeignKey("iteration.id"), nullable = False)
    date = Column(Date, nullable = False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable = False)
    source_request_id = Column(Integer, ForeignKey("request.id"), nullable = False)
    allocated_resource_id = Column(Integer, ForeignKey("resource.id"))
    points = Column(Integer)


def populate_enums(
    metadata: db.MetaData,
    sess: db.orm.Session,
) -> None:
    """
    Function to write defined enum values to their associated tables. This is used during an
    initial database migration or to make dummy databases during testing. If is data in the table,
    no rows are inserted.

    Args:
        metadata: db.MetaData object where the tables are bound to
        sess: active db.orm.Session object already bound to its database engine

    Returns:
        None
    """
    table_enums = [
        (RoleModel, "role", RoleEnum),
    ]

    for table, column, enum in table_enums:
        if sess.query(db.func.count(table.id)).scalar() == 0:
            sess.add_all([table(**{column: item.value}) for item in enum])

