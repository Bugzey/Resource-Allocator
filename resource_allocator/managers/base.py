"""
Base manager object to provide standardized operations
"""

from abc import ABC, abstractmethod
from collections.abc import Collection
from dataclasses import dataclass
from enum import auto, StrEnum
import re
from typing import Any, ClassVar

import sqlalchemy as sa
from sqlalchemy.orm import Session

from resource_allocator.config import Config
from resource_allocator.models import Base


class Operation(StrEnum):
    """
    Filter operation enum. Contains the definitions of all operation types for filtering data
    """
    eq = auto()
    ne = auto()
    gt = auto()
    ge = auto()
    lt = auto()
    le = auto()
    isin = auto()
    notin = auto()
    like = auto()


@dataclass
class Filter:
    """
    Single configured filter operation on a single field

    Value is retained as a scalar unless operations are notin and isin - fields are separated by ,
    """
    field_name: str
    value: Any | list[Any]
    operation: Operation = Operation.eq

    def __post_init__(self):
        #   Transfer operation to a valid enum member
        if self.operation in Operation:
            self.operation = Operation[self.operation]
        else:
            raise ValueError(f"Invalid operation: {self.operation}")

        #   Split fields in case the operation is isin or notin
        if (
            self.operation in (Operation.isin, Operation.notin)
            and not isinstance(self.value, list)
        ):
            self.value = str(self.value).split(",")

    @classmethod
    def from_key_value(cls, key: str, value: Any) -> "Filter":
        """
        Parse a filter key-value pair extracting the field name and operation

        Key format: filter[(field_name)][(optional_operation)]
        """
        pattern = re.compile(r"filter\[(.+?)\](\[.+?\]){0,1}")
        result = re.match(pattern, key)
        if not result:
            raise ValueError(
                "Invalid filter format. Expecting filter[<field_name>] or "
                f"filter[<field_name>][<operation>]. Got: {key}"
            )
        field_name = result.group(1)
        operation = (result.group(2) or "eq").strip("[]")  # Filter post_init handles op validation
        return cls(field_name=field_name, value=value, operation=operation)


@dataclass
class _ContainerBase(Collection):
    def __getitem__(self, index):
        return self.items[index]

    def __contains__(self, item):
        return item in self.items

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


@dataclass
class FilterConfig(_ContainerBase):
    items: list[Filter]

    @classmethod
    def from_request_dict(cls, request_dict: dict) -> "FilterConfig":
        errors = []
        result = []
        for key, value in request_dict.items():
            if "filter" not in key:
                continue

            try:
                cur_result = Filter.from_key_value(key, value)
                result.append(cur_result)
            except ValueError as exc:
                errors.append(exc)

        if errors:
            raise ValueError(f"Error parsing filters: {len(errors)}: {errors}")

        return cls(result)


@dataclass
class OrderBy:
    field_name: str
    ascending: bool = True

    def __post_init__(self):
        self.field_name = str(self.field_name)
        if self.field_name.startswith("-"):
            self.ascending = False
            self.field_name = self.field_name.lstrip("-")


@dataclass
class OrderByConfig(_ContainerBase):
    items: list[OrderBy]

    @classmethod
    def from_request_dict(cls, request_dict: dict) -> OrderByConfig:
        value = request_dict.get("order_by", [])
        if isinstance(value, str):
            value = [value]
        items = [OrderBy(item) for item in value]
        return cls(items)


@dataclass
class BaseManager(ABC):
    """
    Base manager class for standard CRUD-like operations on database tables. Child classes should
    define a class-level property "model" to point to the sqlalchemy ORM table to use

    An SQLAlchemy session should be given on initiation when the Flask object is created

    Class variables:
        model: sqlalchemy ORM table

    Init variables:
        sess: SQLAlchemy session for data access
    """
    sess: Session
    config: Config | None = None

    nested_managers: ClassVar[dict[str, "BaseManager"] | None] = None

    def __post_init__(self):
        if self.nested_managers is None:
            self.nested_managers = {}

    @property
    @abstractmethod
    def model(self) -> Base:
        pass

    def list_single_item(self, id: int) -> Base:
        """
        List properties of a single item.

        Args:
            id: numeric ID of the item to query

        Returns:
            Base - Base model
        """
        item = self.sess.get(self.model, id)  # can be None
        return item

    def list_all_items(
        self,
        filters: FilterConfig | None = None,
        order_by: OrderByConfig | None = None,
        limit: int = 200,
        page: int = 1,
    ) -> list[Base]:

        #   Select
        query = sa.select(self.model)

        #   Build a where clause
        where = []
        for item in filters or []:
            col = getattr(self.model, item.field_name)
            match item.operation:
                case Operation.eq:
                    where.append(col == item.value)
                case Operation.ne:
                    where.append(col != item.value)
                case Operation.gt:
                    where.append(col > item.value)
                case Operation.ge:
                    where.append(col >= item.value)
                case Operation.lt:
                    where.append(col < item.value)
                case Operation.le:
                    where.append(col <= item.value)
                case Operation.isin:
                    where.append(col.in_(item.value))  # already a collection
                case Operation.notin:
                    where.append(col.notin_(item.value))  # already a collection
                case Operation.like:
                    where.append(col.like(item.value))
                case _:
                    raise ValueError(f"Unknown operation: {item.operation}")

        query = query.where(*where)

        #   Pagination
        query = query.offset(limit * (page - 1)).limit(limit)

        #   Ordering
        query = query.order_by(*[
            getattr(self.model, item.field_name)
            if item.ascending
            else getattr(self.model, item.field_name).desc()
            for item
            in order_by or []
        ])

        #   Final result
        items = self.sess.scalars(query).all()
        return items

    def create_item(self, data: dict) -> Base:
        for key in set(self.nested_managers.keys()) & set(data.keys()):
            data[key] = self.nested_managers[key](self.sess).create_item(data[key])

        item = self.model(**data)
        self.sess.add(item)
        self.sess.flush()
        return item

    def delete_item(self, id: int) -> Base:
        item = self.sess.get(self.model, id)  # can be None
        if not item:
            return item

        self.sess.delete(item)
        self.sess.flush()
        return item

    def modify_item(self, id: int, data: dict) -> Base:
        item = self.sess.get(self.model, id)  # can be None
        if not item:
            return item

        for key in set(self.nested_managers.keys()) & set(data.keys()):
            nested_manager = self.nested_managers[key](self.sess)
            nested_item = nested_manager.list_single_item(item.__dict__[key].id)
            if isinstance(nested_item, nested_manager.model):
                data[key] = nested_manager.modify_item(nested_item.id, data[key])
            else:
                data[key] = nested_manager.create_item(data[key])

        result = {
            key: value
            for key, value
            in data.items()
            if key not in self.nested_managers.keys()
        }
        self.sess.execute(
            sa.update(self.model)
            .where(self.model.id == id)
            .values(result)
        )

        self.sess.flush()
        return item
