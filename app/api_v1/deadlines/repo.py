from app.core.base.base_repository import BaseRepository
from app.api_v1.deadlines.models import DeadlinesOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


class DeadlinesRepo(BaseRepository):
    model = DeadlinesOrm


deadlines_repo: DeadlinesOrm = DeadlinesRepo()
