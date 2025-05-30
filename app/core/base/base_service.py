from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, TypeVar, Generic, Type
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from .base_model import Base
from pydantic import BaseModel
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class BaseService:
    def __init__(self, repository: BaseRepository, schema_out: type[BaseModel] = None):
        self.repository = repository
        self.schema_out = schema_out

    def _to_schema(self, obj: Base) -> BaseModel:
        if not self.schema_out:
            return obj
        return self.schema_out.model_validate(obj)

    def _to_schema_many(self, objs: list[Base]) -> list[BaseModel]:
        return [self._to_schema(obj) for obj in objs]

    async def find_one_or_none_by_pid(
        self, session: AsyncSession, data_pid: int
    ) -> BaseModel | None:
        """Находит обьект по pid = data_pid\n
        return: Найденный ORM обьект. None если не нашел"""

        orm_obj = await self.repository.find_one_or_none_by_pid(
            session=session, data_pid=data_pid
        )
        return self._to_schema(orm_obj) if orm_obj else None

    async def find_one_or_none(
        self, session: AsyncSession, filters: BaseModel
    ) -> BaseModel | None:
        """Находит обьект по фильтрам filters.\n
        return: Найденный ORM обьект. None если не нашел"""

        orm_obj = await self.repository.find_one_or_none(
            session=session, filters=filters
        )
        return self._to_schema(orm_obj) if orm_obj else None

    async def find_all(
        self,
        session: AsyncSession,
        filters: BaseModel | None = None,
        options: list | None = None,
    ) -> list[BaseModel]:
        """Находит список обьектов по фильтрам filters.\n
        return: Список найденных ORM обьектов. None если не нашел"""

        orm_objs = await self.repository.find_all(
            session=session, filters=filters, options=options
        )
        return self._to_schema_many(orm_objs)

    async def add(self, session: AsyncSession, values: BaseModel) -> BaseModel:
        """Добавляет обьект со значениями values.\n
        return: Добавленный обьект"""

        orm_obj = await self.repository.add(session=session, values=values)
        return self._to_schema(orm_obj) if orm_obj else None

    async def add_many(
        self, session: AsyncSession, instances: list[BaseModel]
    ) -> list[Base]:
        """Добавляет обьекты из списка instances.\n
        return: Список добавленных обьектов"""

        orm_objs = await self.repository.add_many(session=session, instances=instances)
        return self._to_schema_many(orm_objs)

    async def update(
        self, session: AsyncSession, filters: BaseModel, values: BaseModel
    ) -> int:
        """Обновляет обьект со значениями filters на новые значения values.\n
        return: количество измененных обьектов"""
        return await self.repository.update(
            session=session, filters=filters, values=values
        )

    async def delete(self, session: AsyncSession, filters: BaseModel) -> int:
        """Удаляет обьект со значениями filters.\n
        return: количество удаленых обьектов"""

        return await self.repository.delete(session=session, filters=filters)

    async def count(
        self, session: AsyncSession, filters: BaseModel | None = None
    ) -> int:
        """Считает количество обьектов со значениями filters.\n
        return: количество обьектов"""

        return await self.repository.count(session=session, filters=filters)

    async def bulk_update(self, session: AsyncSession, records: List[BaseModel]) -> int:
        """Обновляет все записи из records, где id = record.id, на новые значения record .\n
        return: количество обновленных обьектов"""
        return await self.bulk_update(session=session, records=records)
