from app.api_v1.deadlines.repo import DeadlinesRepo
from app.api_v1.deadlines.repo import deadlines_repo
from app.api_v1.deadlines.schemas import DeadlineRead
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


class DeadlinesService(BaseService):
    def __init__(self, repository: DeadlinesRepo, schemas_out=DeadlineRead):
        self.repository = repository
        self.schema_out = schemas_out
        super().__init__(repository=self.repository, schema_out=self.schema_out)

    async def get_deadline_by_date_to(
        self,
        session: AsyncSession,
        date: datetime,
        author_id: int,
        interval_seconds: int,
    ):
        return await self.repository.get_deadline_by_date_to(
            session=session,
            date=date,
            author_id=author_id,
            interval_seconds=interval_seconds,
        )

    async def get_deadline_by_date_from(
        self,
        session: AsyncSession,
        date: datetime,
        author_id: int,
        interval_seconds: int,
    ):
        return await self.repository.get_deadline_by_date_from(
            session=session,
            date=date,
            author_id=author_id,
            interval_seconds=interval_seconds,
        )


deadlines_service: DeadlinesService = DeadlinesService(repository=deadlines_repo)
