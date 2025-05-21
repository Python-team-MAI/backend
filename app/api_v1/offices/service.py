from app.api_v1.offices.repo import OfficesRepo
from app.api_v1.offices.repo import offices_repo
from app.api_v1.offices.schemas import OfficeRead
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class OfficesService(BaseService):
    def __init__(self, repository: OfficesRepo, schemas_out = OfficeRead):
        self.repository = repository
        self.schema_out = schemas_out
        super().__init__(repository=self.repository, schema_out=self.schema_out)


offices_service: OfficesService = OfficesService(repository=offices_repo)