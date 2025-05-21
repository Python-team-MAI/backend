from app.api_v1.deadlines.repo import DeadlinesRepo
from app.api_v1.deadlines.repo import deadlines_repo
from app.api_v1.deadlines.schemas import DeadlineRead
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class DeadlinesService(BaseService):
    def __init__(self, repository: DeadlinesRepo, schemas_out = DeadlineRead):
        self.repository = repository
        self.schema_out = schemas_out
        super().__init__(repository=self.repository, schema_out=self.schema_out)


deadlines_service: DeadlinesService = DeadlinesService(repository=deadlines_repo)