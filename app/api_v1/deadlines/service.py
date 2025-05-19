from app.api_v1.deadlines.repo import DeadlinesRepo
from app.api_v1.deadlines.repo import deadlines_repo
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class DeadlinesService(BaseService):
    def __init__(self, repository: DeadlinesRepo):
        self.repository = repository
        super().__init__(repository=self.repository)


deadlines_service: DeadlinesService = DeadlinesService(repository=deadlines_repo)