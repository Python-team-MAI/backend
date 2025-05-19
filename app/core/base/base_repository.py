from typing import List, TypeVar, Generic, Type
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, func
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from .base_model import Base

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    model: Type[T] = None

    def __init__(self):
        if self.model is None:
            raise ValueError("Модель должна быть указана в дочернем классе")

    async def find_one_or_none_by_pid(self, session: AsyncSession, data_pid: int):
        try:
            query = select(self.model).filter_by(pid=data_pid)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {self.model.__name__} с ID {data_pid} {'найдена' if record else 'не найдена'}."
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {data_pid}: {e}")
            raise

    async def find_one_or_none(self, session: AsyncSession, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(
            f"Поиск одной записи {self.model.__name__} по фильтрам: {filter_dict}"
        )
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {'найдена' if record else 'не найдена'} по фильтрам: {filter_dict}"
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
            raise

    async def find_all(self, session: AsyncSession, filters: BaseModel | None = None):
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(
            f"Поиск всех записей {self.model.__name__} по фильтрам: {filter_dict}"
        )
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await session.execute(query)
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей.")
            return records
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при поиске всех записей по фильтрам {filter_dict}: {e}"
            )
            raise

    async def add(self, session: AsyncSession, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(
            f"Добавление записи {self.model.__name__} с параметрами: {values_dict}"
        )
        try:
            new_instance = self.model(**values_dict)
            session.add(new_instance)
            logger.info(f"Запись {self.model.__name__} успешно добавлена.")
            await session.flush()
            return new_instance
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении записи: {e}")
            raise

    async def add_many(self, session: AsyncSession, instances: List[BaseModel]):
        values_list = [item.model_dump(exclude_unset=True) for item in instances]
        logger.info(
            f"Добавление нескольких записей {self.model.__name__}. Количество: {len(values_list)}"
        )
        try:
            new_instances = [self.model(**values) for values in values_list]
            session.add_all(new_instances)
            logger.info(f"Успешно добавлено {len(new_instances)} записей.")
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
        logger.info(
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
            logger.info(f"Обновлено {result.rowcount} записей.")
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении записей: {e}")
            raise

    async def delete(self, session: AsyncSession, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Удаление записей {self.model.__name__} по фильтру: {filter_dict}")
        if not filter_dict:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError("Нужен хотя бы один фильтр для удаления.")
        try:
            query = sqlalchemy_delete(self.model).filter_by(**filter_dict)
            result = await session.execute(query)
            logger.info(f"Удалено {result.rowcount} записей.")
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении записей: {e}")
            raise

    async def count(self, session: AsyncSession, filters: BaseModel | None = None):
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(
            f"Подсчет количества записей {self.model.__name__} по фильтру: {filter_dict}"
        )
        try:
            query = select(func.count(self.model.pid)).filter_by(**filter_dict)
            result = await session.execute(query)
            count = result.scalar()
            logger.info(f"Найдено {count} записей.")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подсчете записей: {e}")
            raise

    async def bulk_update(self, session: AsyncSession, records: List[BaseModel]):
        logger.info(f"Массовое обновление записей {self.model.__name__}")
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

            logger.info(f"Обновлено {updated_count} записей")
            await session.flush()
            return updated_count
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при массовом обновлении: {e}")
            raise
