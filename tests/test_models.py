"""
Models test case
"""

import unittest

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from resource_allocator.models import Base, UserModel


class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite://")
        with self.engine.connect() as con:
            con.execute(text("attach database \":memory:\" as resource_allocator"))
            con.execute(text("attach database \":memory:\" as resource_allocator_test"))
            con.commit()

    def test_create_all(self):
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as sess:
            data = sess.scalars(select(UserModel)).all()

        self.assertEqual(data, [])
