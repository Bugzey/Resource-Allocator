"""
Models test case
"""

import datetime as dt
import unittest

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from resource_allocator.models import Base, UserModel, IterationModel


class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite://")
        with self.engine.connect() as con:
            con.execute(text("attach database \":memory:\" as resource_allocator"))
            con.execute(text("attach database \":memory:\" as resource_allocator_test"))
            con.commit()

        Base.metadata.create_all(self.engine)

    def test_create_all(self):
        with Session(self.engine) as sess:
            data = sess.scalars(select(UserModel)).all()

        self.assertEqual(data, [])

    def test_repr(self):
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as sess:
            item = IterationModel(start_date=dt.date(2025, 1, 1), end_date=dt.date(2025, 1, 15))
            sess.add(item)
            sess.flush()

        result = str(item)
        self.assertIn("IterationModel(", result)
        self.assertIn("id=1", result)
        self.assertIn("requests=...", result)
