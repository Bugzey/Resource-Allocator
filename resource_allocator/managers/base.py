"""
Base manager object to provide standardized operations
"""

from abc import ABC, abstractmethod

import sqlalchemy as db

from resource_allocator.db import sess

class BaseManager(ABC):
    """
    Base manager class for standard CRUD-like operations on database tables. Child classes should
    define a class-level property "model" to point to the sqlalchemy ORM table to use

    Properties:
        model: sqlalchemy ORM table
    """
    @property
    @abstractmethod
    def model(cls) -> db.Table:...

    @classmethod
    def list_single_item(cls, id: int) -> db.Table:
        """
        List properties of a single item.

        Args:
            id: numeric ID of the item to query

        Returns:
            db.Table
        """
        item = sess.get(cls.model, id)
        if not item:
            return f"{cls.model.__tablename__} not found: {id}", 404

        return item

    @classmethod
    def list_all_items(cls) -> list[db.Table]:
        items = sess.query(cls.model).all()
        return items

    @classmethod
    def create_item(cls, data: dict) -> db.Table:
        item = cls.model(**data)
        sess.add(item)
        sess.flush()
        return item

    @classmethod
    def delete_item(cls, id: int) -> db.Table:
        item = sess.get(cls.model, id)
        if not item:
            return f"{cls.model.__tablename__} not found", 404

        sess.delete(item)
        sess.flush()
        return item

    @classmethod
    def modify_item(cls, id: int, data: dict) -> db.Table:
        item = sess.get(cls.model, id)
        if not item:
            return f"{cls.model.__tablename__} not found", 404

        sess.execute(
            db.update(cls.model) \
            .where(cls.model.id == id) \
            .values(**data)
        )

        sess.flush()
        return item

