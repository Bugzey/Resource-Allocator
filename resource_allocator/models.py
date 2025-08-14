"""
Database models creation
"""

import datetime as dt
from enum import Enum

import sqlalchemy as db
from sqlalchemy import (
    ForeignKey,
    func,
    inspect,
    UniqueConstraint,
)
from sqlalchemy import orm
from sqlalchemy.orm import (
    DeclarativeBase,
    relationship,
    Mapped,
    mapped_column,
    ColumnProperty,
)


metadata = db.MetaData(schema="resource_allocator")


class Base(DeclarativeBase):
    metadata = metadata
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    created_time: Mapped[dt.datetime] = mapped_column(server_default=func.now())
    updated_time: Mapped[dt.datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self):
        mapper = inspect(self.__class__)
        cols = {
            f"{key}={self.__dict__.get(key) if isinstance(value, ColumnProperty) else '...'}"
            for key, value
            in mapper.attrs.items()
        }
        return (
            f"{self.__class__.__name__}("
            f"{', '.join(cols)}"
            ")"
        )


class RoleEnum(Enum):
    user = "user"
    admin = "admin"


class RoleModel(Base):
    __tablename__ = "role"
    role: Mapped[str] = mapped_column(unique=True)


class UserModel(Base):
    __tablename__ = "user"
    __table_args__ = (
        db.CheckConstraint(
            "password_hash is not NULL or is_external is TRUE",
            name="check_internal_or_external"
        ),
    )
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str | None]
    first_name: Mapped[str]
    last_name: Mapped[str]
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))
    role: Mapped["RoleModel"] = relationship()
    is_external: Mapped[bool] = mapped_column(server_default="false")


class ResourceGroupModel(Base):
    __tablename__ = "resource_group"
    name: Mapped[str] = mapped_column(unique=True)
    is_top_level: Mapped[bool] = mapped_column(server_default="false")
    top_resource_group_id: Mapped[int | None] = mapped_column(ForeignKey("resource_group.id"))
    top_resource_group: Mapped["ResourceGroupModel"] = relationship()
    image_id: Mapped[int | None] = mapped_column(ForeignKey("image.id"))
    image: Mapped["ImageModel"] = relationship()
    image_properties_id: Mapped[int | None] = mapped_column(ForeignKey("image_properties.id"))
    image_properties: Mapped["ImagePropertiesModel"] = relationship()


class ResourceToGroupModel(Base):
    __tablename__ = "resource_to_group"
    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id"))
    resource_group_id: Mapped[int] = mapped_column(ForeignKey("resource_group.id"))


class ResourceModel(Base):
    __tablename__ = "resource"
    name: Mapped[str] = mapped_column(unique=True)
    top_resource_group_id: Mapped[int] = mapped_column(ForeignKey("resource_group.id"))
    top_resource_group: Mapped["ResourceGroupModel"] = relationship()
    resource_groups: Mapped[list["ResourceGroupModel"]] = relationship(
        secondary=ResourceToGroupModel.__table__,
    )
    image_id: Mapped[int | None] = mapped_column(ForeignKey("image.id"))
    image: Mapped["ImageModel"] = relationship()
    image_properties_id: Mapped[int | None] = mapped_column(ForeignKey("image_properties.id"))
    image_properties: Mapped["ImagePropertiesModel"] = relationship()


class IterationModel(Base):
    __tablename__ = "iteration"
    start_date: Mapped[dt.date]
    end_date: Mapped[dt.date]
    is_allocated: Mapped[bool] = mapped_column(server_default="false")
    requests: Mapped[list["RequestModel"]] = relationship(back_populates="iteration")
    allocations: Mapped[list["AllocationModel"]] = relationship(back_populates="iteration")


class RequestStatusEnum(Enum):
    new = "New"
    completed = "Completed"
    declined = "Declined"


class RequestStatusModel(Base):
    __tablename__ = "request_status"
    request_status: Mapped[str]


class RequestModel(Base):
    __tablename__ = "request"
    iteration_id: Mapped[int] = mapped_column(ForeignKey("iteration.id"))
    iteration: Mapped["IterationModel"] = relationship(back_populates="requests")
    requested_date: Mapped[dt.date]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    requested_resource_id: Mapped[int | None] = mapped_column(ForeignKey("resource.id"))
    requested_resource: Mapped["ResourceModel"] = relationship()
    requested_resource_group_id: Mapped[int | None] = mapped_column(ForeignKey("resource_group.id"))
    requested_resource_group: Mapped["ResourceGroupModel"] = relationship()
    request_status_id: Mapped[int] = mapped_column(
        ForeignKey("request_status.id", name="request_request_status_id_fkey"),
    )
    request_status: Mapped["RequestStatusModel"] = relationship()
    allocation: Mapped["AllocationModel"] = relationship()


class AllocationModel(Base):
    __tablename__ = "allocation"
    __table_args__ = (
        UniqueConstraint(
            "iteration_id", "date", "allocated_resource_id",
            name="allocation_iteration_id_date_allocated_resource_id_key",
        ),
    )
    iteration: Mapped["IterationModel"] = relationship(back_populates="allocations")
    iteration_id: Mapped[int] = mapped_column(ForeignKey("iteration.id"))
    date: Mapped[dt.date]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    source_request_id: Mapped[int] = mapped_column(ForeignKey("request.id"))
    allocated_resource_id: Mapped[int | None] = mapped_column(ForeignKey("resource.id"))
    allocated_resource: Mapped[ResourceModel | None] = relationship()
    points: Mapped[int | None]


class ImageTypeModel(Base):
    __tablename__ = "image_type"
    image_type: Mapped[str] = mapped_column(unique=True)


class ImageModel(Base):
    __tablename__ = "image"
    image_data: Mapped[bytes]
    image_type_id: Mapped[int] = mapped_column(ForeignKey("image_type.id"))
    image_type: Mapped["ImageTypeModel"] = relationship()
    size_bytes: Mapped[int]
    resource_group: Mapped["ResourceGroupModel"] = relationship(back_populates="image")
    resource: Mapped["ResourceModel"] = relationship(back_populates="image")


class ImagePropertiesModel(Base):
    __tablename__ = "image_properties"
    box_x: Mapped[float]
    box_y: Mapped[float]
    box_width: Mapped[float]
    box_height: Mapped[float]
    box_rotation: Mapped[float]


def populate_enums(
    sess: orm.Session,
) -> None:
    """
    Function to write defined enum values to their associated tables. This is used during an
    initial database migration or to make dummy databases during testing. If is data in the table,
    no rows are inserted.

    Args:
        sess: active orm.Session object already bound to its database engine

    Returns:
        None
    """
    table_enums = [
        (RoleModel, "role", RoleEnum),
        (RequestStatusModel, "request_status", RequestStatusEnum),
    ]

    for table, column, enum in table_enums:
        if sess.query(func.count(table.id)).scalar() == 0:
            sess.add_all([table(**{column: item.value}) for item in enum])
