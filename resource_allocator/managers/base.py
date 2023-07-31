"""
Base manager object to provide standardized operations
"""

from abc import ABC, abstractmethod

import sqlalchemy as db

from resource_allocator.db import get_session


class BaseManager(ABC):
    """
    Base manager class for standard CRUD-like operations on database tables. Child classes should
    define a class-level property "model" to point to the sqlalchemy ORM table to use

    Properties:
        model: sqlalchemy ORM table
    """
    @classmethod
    @property
    def sess(cls) -> db.orm.Session:
        return get_session()

    @property
    @classmethod
    @abstractmethod
    def model(cls) -> db.Table:
        pass

    nested_managers: dict[str, "BaseManager"] = dict()

    @classmethod
    def list_single_item(cls, id: int) -> db.Table:
        """
        List properties of a single item.

        Args:
            id: numeric ID of the item to query

        Returns:
            db.Table
        """
        item = cls.sess.get(cls.model, id)
        if not item:
            return f"{cls.model.__tablename__} not found: {id}", 404

        return item

    @classmethod
    def list_all_items(cls) -> list[db.Table]:
        items = cls.sess.query(cls.model).all()
        return items

    @classmethod
    def create_item(cls, data: dict) -> db.Table:
        for key in set(cls.nested_managers.keys()) & set(data.keys()):
            data[key] = cls.nested_managers[key].create_item(data[key])

        item = cls.model(**data)
        cls.sess.add(item)
        cls.sess.flush()
        return item

    @classmethod
    def delete_item(cls, id: int) -> db.Table:
        item = cls.sess.get(cls.model, id)
        if not item:
            return f"{cls.model.__tablename__} not found", 404

        cls.sess.delete(item)
        cls.sess.flush()
        return item

    @classmethod
    def modify_item(cls, id: int, data: dict) -> db.Table:
        item = cls.sess.get(cls.model, id)
        if not item:
            return f"{cls.model.__tablename__} not found", 404

        for key in set(cls.nested_managers.keys()) & set(data.keys()):
            nested_manager = cls.nested_managers[key]
            nested_item = nested_manager.list_single_item(item.__dict__[key].id)
            if isinstance(nested_item, nested_manager.model):
                data[key] = nested_manager.modify_item(nested_item.id, data[key])
            else:
                data[key] = nested_manager.create_item(data[key])

        cls.sess.execute(
            db.update(cls.model)
            .values(**{
                key: value
                for key, value
                in data.items()
                if key not in cls.nested_managers.keys()
            })
        )

        cls.sess.flush()
        return item
