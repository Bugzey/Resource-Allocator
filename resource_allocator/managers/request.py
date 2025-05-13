"""
Request-related managers
"""

from sqlalchemy import select

from resource_allocator.models import RequestModel, RequestStatusEnum, RequestStatusModel
from resource_allocator.managers.base import BaseManager


class RequestManager(BaseManager):
    model = RequestModel

    @classmethod
    def create_item(cls, data: dict):
        if "request_status_id" not in data:
            query = (
                select(RequestStatusModel.id)
                .where(RequestStatusModel.request_status == RequestStatusEnum.new.value)
            )
            data["request_status_id"] = cls.sess.execute(query).scalar()

        super().create_item(data)
