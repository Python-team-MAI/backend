from app.api_v1.offices.repo import OfficesRepo
from app.api_v1.offices.repo import offices_repo
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class OfficesService(BaseService):
    def __init__(self, repository: OfficesRepo):
        self.repository = repository
        super().__init__(repository=self.repository)


offices_service: OfficesService = OfficesService(repository=offices_repo)