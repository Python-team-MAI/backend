from contextlib import asynccontextmanager
from typing import Callable, Optional
from fastapi import Depends
import logging
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from typing_extensions import AsyncGenerator
from sqlalchemy import text
from functools import wraps

from app.core.base.base_model import async_session_maker


class DatabaseSessionManager:
    """
    Менеджер для работы с сессиями базы данных. Позволяет управлять сессиями,
    транзакциями и предоставляет зависимости FastAPI для удобного внедрения сессий.
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.async_session_maker = session_maker
        self.logger = logging.getLogger(__name__)

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Создает новую сессию базы данных.

        В этом методе создается асинхронная сессия базы данных.
        В случае ошибки логирует ее и повторно поднимает исключение,
        а также гарантирует закрытие сессии при завершении работы.

        Выходной тип: Асинхронный генератор сессии `AsyncSession`.
        """
        try:
            async with self.async_session_maker() as session:
                yield session
        except Exception as e:
            self.logger.error(f"Не удалось создать сессию базы данных: {str(e)}")
            raise
        finally:
            await session.close()

    @asynccontextmanager
    async def managed_transaction(
        self, session: AsyncSession
    ) -> AsyncGenerator[None, None]:
        """
        Управляет транзакцией, осуществляя коммит или откат при ошибке.

        Этот метод принимает существующую сессию и выполняет коммит по завершении транзакции.
        Если возникает исключение, происходит откат транзакции и логирование ошибки.

        Параметр:
        - `session`: Текущая асинхронная сессия базы данных `AsyncSession`.

        Выходной тип: Асинхронный генератор.
        """
        try:
            yield
            await session.commit()
        except Exception as e:
            await session.rollback()
            self.logger.exception(f"Транзакция не удалась: {str(e)}")
            raise

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Зависимость для FastAPI, предоставляющая сессию без управления транзакцией.

        Асинхронный генератор для использования с FastAPI в качестве зависимости,
        который предоставляет сессию для выполнения запросов к базе данных.

        Выходной тип: Асинхронный генератор сессии `AsyncSession`.
        """
        async with self.get_session() as session:
            yield session

    async def get_db_with_transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Зависимость для FastAPI, предоставляющая сессию с управлением транзакцией.

        Асинхронный генератор для использования с FastAPI в качестве зависимости,
        который предоставляет сессию, автоматически выполняя коммит по завершении транзакции
        или откат в случае ошибки.

        Выходной тип: Асинхронный генератор сессии `AsyncSession`.
        """
        async with self.get_session() as session:
            async with self.managed_transaction(session):
                yield session

    def connection(self, isolation_level: Optional[str] = None, commit: bool = True):
        """
        Декоратор для управления сессией и дополнительными настройками транзакции.

        Позволяет добавлять сессию в метод с возможностью указания уровня изоляции транзакции.
        Если `commit=True`, выполняется коммит в конце метода, иначе коммит не выполняется.

        Параметры:
        - `isolation_level` (опционально): Уровень изоляции для транзакции (например, "SERIALIZABLE").
        - `commit` (по умолчанию True): Определяет, будет ли выполняться коммит после метода.

        Возвращает:
        - Декорированный асинхронный метод с дополнительными параметрами управления транзакцией.
        """

        def decorator(method):
            @wraps(method)
            async def wrapper(*args, **kwargs):
                async with self.async_session_maker() as session:
                    try:
                        # Устанавливаем уровень изоляции, если он указан
                        if isolation_level:
                            await session.execute(
                                text(
                                    f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"
                                )
                            )

                        # Выполняем декорируемый метод
                        result = await method(*args, session=session, **kwargs)

                        # Выполняем коммит, если параметр commit=True
                        if commit:
                            await session.commit()

                        return result
                    except Exception as e:
                        await session.rollback()  # Откатываем транзакцию при ошибке
                        raise e  # Поднимаем исключение дальше
                    finally:
                        await session.close()  # Закрываем сессию

            return wrapper

        return decorator

    @property
    def session_dependency(self) -> Callable:
        """
        Зависимость FastAPI для внедрения сессии без управления транзакцией.

        Возвращает:
        - Зависимость для FastAPI, которая предоставляет асинхронную сессию `AsyncSession`.
        """
        return Depends(self.get_db)

    @property
    def transaction_session_dependency(self) -> Callable:
        """
        Зависимость FastAPI для внедрения сессии с управлением транзакцией.

        Возвращает:
        - Зависимость для FastAPI, которая предоставляет асинхронную сессию `AsyncSession`
          с автоматическим управлением транзакцией (коммит или откат).
        """
        return Depends(self.get_db_with_transaction)


# Создание экземпляра DatabaseSessionManager
session_manager: DatabaseSessionManager = DatabaseSessionManager(async_session_maker)

# не делает коммит
SessionDep: AsyncSession = session_manager.session_dependency

# делает коммит
TransactionSessionDep: AsyncSession = session_manager.transaction_session_dependency


# Пример использования декоратора
# @db_manager.connection(isolation_level="SERIALIZABLE", commit=True)
# async def example_method(*args, session: AsyncSession, **kwargs):
#     # Основная логика метода
#     pass
