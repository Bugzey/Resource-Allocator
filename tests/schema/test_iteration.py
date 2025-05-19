import datetime as dt
import unittest
from unittest.mock import MagicMock, patch

from marshmallow import ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.sql.ddl import CreateTable
from sqlalchemy.orm import Session

from resource_allocator.schemas.iteration import IterationRequestSchema
from resource_allocator.models import IterationModel


class IterationRequestSchemaTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        with self.engine.connect() as con:
            con.execute(text('attach database ":memory:" as resource_allocator'))
            con.execute(CreateTable(IterationModel.__table__))

        self.sess = Session(self.engine)
        self.sess.add(IterationModel(start_date=dt.date(2025, 2, 1), end_date=dt.date(2025, 2, 10)))
        self.sess.flush()

    @staticmethod
    def patch_session(fun):
        def inner(self, *args, **kwargs):
            @patch(
                "resource_allocator.schemas.iteration.get_session",
                MagicMock(return_value=self.sess),
            )
            def more_inner(self, *args, **kwargs):
                return fun(self, *args, **kwargs)

        return inner

    @patch_session
    def test_overlap(self):
        schema = IterationRequestSchema()

        #   Left
        self.assertEqual(
            schema.validate({"start_date": "2025-02-11", "end_date": "2025-02-18"}),
            {},
        )

        #   Right
        self.assertNotEqual(
            schema.validate({"start_date": "2025-01-15", "end_date": "2025-02-10"}),
            {},
        )

        #   Inner
        self.assertNotEqual(
            schema.validate({"start_date": "2025-02-05", "end_date": "2025-02-15"}),
            {},
        )

        #   Outer
        self.assertNotEqual(
            schema.validate({"start_date": "2025-01-05", "end_date": "2025-02-08"}),
            {},
        )
        self.assertNotEqual(
            schema.validate({"start_date": "2025-01-15", "end_date": "2025-02-15"}),
            {},
        )

    def test_validate_continuity(self):
        schema = IterationRequestSchema()
        self.assertIsNone(
            schema.validate_continuity({"start_date": "2025-01-01", "end_date": "2025-01-15"}),
        )
        self.assertRaises(
            ValidationError,
            schema.validate_continuity,
            {"start_date": "2025-01-15", "end_date": "2025-01-01"},
        )
