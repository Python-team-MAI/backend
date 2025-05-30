from app.core.base.base_repository import BaseRepository
from app.api_v1.deadlines.models import DeadlinesOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from datetime import datetime, timedelta


class DeadlinesRepo(BaseRepository):
    model = DeadlinesOrm

    async def get_deadline_by_date_from(
        self,
        session: AsyncSession,
        date: datetime,
        author_id: int,
        interval_seconds: int,
    ):

        result = await session.execute(
            select(DeadlinesOrm).where(
                and_(
                    DeadlinesOrm.date_from >= date,
                    DeadlinesOrm.date_from < date + timedelta(seconds=interval_seconds),
                    DeadlinesOrm.author_id == author_id,
                )
            )
        )
        return result.scalars().all()

    async def get_deadline_by_date_to(
        self,
        session: AsyncSession,
        date: datetime,
        author_id: int,
        interval_seconds: int,
    ):

        result = await session.execute(
            select(DeadlinesOrm).where(
                and_(
                    DeadlinesOrm.date_to >= date,
                    DeadlinesOrm.date_to < date + timedelta(seconds=interval_seconds),
                    DeadlinesOrm.author_id == author_id,
                )
            )
        )
        return result.scalars().all()


deadlines_repo: DeadlinesOrm = DeadlinesRepo()
