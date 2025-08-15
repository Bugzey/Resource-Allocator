"""
Iteration-related request schemas
"""

from marshmallow import (
    Schema,
    ValidationError,
    fields,
    validates_schema,
)
from sqlalchemy import select, and_

from resource_allocator.db import get_session
from resource_allocator.models import IterationModel
from resource_allocator.schemas.base import BaseSchema


class IterationRequestSchema(Schema):
    id = fields.Integer()
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    @validates_schema
    def validate_continuity(self, data, **kwargs):
        if data["start_date"] >= data["end_date"]:
            raise ValidationError("end_date must be later than start_date")

    @validates_schema
    def validate_no_overlap(self, data, **kwargs):
        sess = get_session()
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        existing = (
            sess.scalars(
                select(IterationModel)
                .where(
                    and_(
                        start_date <= IterationModel.end_date,
                        end_date >= IterationModel.start_date,
                        IterationModel.id != data.get("id"),
                    )
                )
            )
            .first()
        )
        if existing:
            raise ValidationError(
                f"Dates fall within an existing iteration: id: {existing.id}, "
                f"start_date: {existing.start_date}, end_date: {existing.end_date}"
            )


class IterationResponseSchema(BaseSchema, IterationRequestSchema):
    is_allocated = fields.Boolean()
