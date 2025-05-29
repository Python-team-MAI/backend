from typing import List, TypeVar, Generic, Type
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, func
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from .base_model import Base
from app.api_v1.utils.setup_logging import setup_logging
logger = setup_logging(__name__)

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    model: Type[T] = None

    def __init__(self):
        if self.model is None:
            raise ValueError("Модель должна быть указана в дочернем классе")

    async def find_one_or_none_by_id(self, session: AsyncSession, data_id: int):
        try:
            query = select(self.model).filter_by(id=data_id)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {self.model.__name__} с ID {data_id} {'найдена' if record else 'не найдена'}."
            logger.debug(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {data_id}: {e}")
            raise

    async def find_one_or_none(self, session: AsyncSession, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.debug(
            f"Поиск одной записи {self.model.__name__} по фильтрам: {filter_dict}"
        )
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {'найдена' if record else 'не найдена'} по фильтрам: {filter_dict}"
            logger.debug(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
            raise

    async def find_all(self, session: AsyncSession, filters: BaseModel | None = None, options: list = None):
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.debug(
            f"Поиск всех записей {self.model.__name__} по фильтрам: {filter_dict}"
        )
        try:
            query = select(self.model).filter_by(**filter_dict)
            if options:
                for opt in options:
                    query = query.options(opt)
            result = await session.execute(query)
            records = result.scalars().all()
            logger.debug(f"Найдено {len(records)} записей.")
            return records
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при поиске всех записей по фильтрам {filter_dict}: {e}"
            )
            raise

    async def add(self, session: AsyncSession, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        logger.debug(
            f"Добавление записи {self.model.__name__} с параметрами: {values_dict}"
        )
        try:
            new_instance = self.model(**values_dict)
            session.add(new_instance)
            logger.debug(f"Запись {self.model.__name__} успешно добавлена.")
            await session.flush()
            return new_instance
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении записи: {e}")
            raise

    async def add_many(self, session: AsyncSession, instances: List[BaseModel]):
        values_list = [item.model_dump(exclude_unset=True) for item in instances]
        logger.debug(
            f"Добавление нескольких записей {self.model.__name__}. Количество: {len(values_list)}"
        )
        try:
            new_instances = [self.model(**values) for values in values_list]
            session.add_all(new_instances)
            logger.debug(f"Успешно добавлено {len(new_instances)} записей.")
            logger.debug(
                f"Транзакция: {'ACTIVE' if session.in_transaction() else 'INACTIVE'}"
            )
            await session.flush()
            return new_instances
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении нескольких записей: {e}")
            raise

    async def update(
        self, session: AsyncSession, filters: BaseModel, values: BaseModel
    ):
        """filters: Фильтры определяют обьекты, которые будут обновляться\n
        values: Определяют какие значения вместо каких полей подставить"""
        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = values.model_dump(exclude_unset=True)
        logger.debug(
            f"Обновление записей {self.model.__name__} по фильтру: {filter_dict} с параметрами: {values_dict}"
        )
        try:
            query = (
                sqlalchemy_update(self.model)
                .where(*[getattr(self.model, k) == v for k, v in filter_dict.items()])
                .values(**values_dict)
                .execution_options(synchronize_session="fetch")
            )
            result = await session.execute(query)
            logger.debug(f"Обновлено {result.rowcount} записей.")
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении записей: {e}")
            raise

    async def delete(self, session: AsyncSession, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.debug(
            f"Удаление записей {self.model.__name__} по фильтру: {filter_dict}"
        )
        if not filter_dict:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError("Нужен хотя бы один фильтр для удаления.")
        try:
            query = sqlalchemy_delete(self.model).filter_by(**filter_dict)
            result = await session.execute(query)
            logger.debug(f"Удалено {result.rowcount} записей.")
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении записей: {e}")
            raise

    async def count(self, session: AsyncSession, filters: BaseModel | None = None):
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.debug(
            f"Подсчет количества записей {self.model.__name__} по фильтру: {filter_dict}"
        )
        try:
            query = select(func.count(self.model.pid)).filter_by(**filter_dict)
            result = await session.execute(query)
            count = result.scalar()
            logger.debug(f"Найдено {count} записей.")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подсчете записей: {e}")
            raise

    async def bulk_update(self, session: AsyncSession, records: List[BaseModel]):
        logger.debug(f"Массовое обновление записей {self.model.__name__}")
        try:
            updated_count = 0
            for record in records:
                record_dict = record.model_dump(exclude_unset=True)
                if "pid" not in record_dict:
                    continue

                update_data = {k: v for k, v in record_dict.items() if k != "pid"}
                stmt = (
                    sqlalchemy_update(self.model)
                    .filter_by(id=record_dict["pid"])
                    .values(**update_data)
                )
                result = await session.execute(stmt)
                updated_count += result.rowcount

            logger.debug(f"Обновлено {updated_count} записей")
            await session.flush()
            return updated_count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при массовом обновлении: {e}")
            raise
