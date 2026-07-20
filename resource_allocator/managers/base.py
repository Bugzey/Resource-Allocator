"""
Base manager object to provide standardized operations
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from flask.views import MethodView
import sqlalchemy as db
from sqlalchemy.orm import Session

from resource_allocator.config import Config


@dataclass
class BaseManager(MethodView, ABC):
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
    def model(self) -> db.Table:
        pass

    def list_single_item(self, id: int) -> db.Table:
        """
        List properties of a single item.

        Args:
            id: numeric ID of the item to query

        Returns:
            db.Table
        """
        item = self.sess.get(self.model, id)  # can be None
        return item

    def list_all_items(self) -> list[db.Table]:
        items = self.sess.query(self.model).all()
        return items

    def create_item(self, data: dict) -> db.Table:
        for key in set(self.nested_managers.keys()) & set(data.keys()):
            data[key] = self.nested_managers[key](self.sess).create_item(data[key])

        item = self.model(**data)
        self.sess.add(item)
        self.sess.flush()
        return item

    def delete_item(self, id: int) -> db.Table:
        item = self.sess.get(self.model, id)  # can be None
        if not item:
            return item

        self.sess.delete(item)
        self.sess.flush()
        return item

    def modify_item(self, id: int, data: dict) -> db.Table:
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
            db.update(self.model)
            .where(self.model.id == id)
            .values(result)
        )

        self.sess.flush()
        return item
