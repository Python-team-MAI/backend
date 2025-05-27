from app.api_v1.offices.repo import OfficesRepo
from app.api_v1.offices.repo import offices_repo
from app.api_v1.offices.schemas import OfficeRead
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
import json
from typing import Any


class OfficesService(BaseService):
    def __init__(self, repository: OfficesRepo, schemas_out=OfficeRead):
        self.repository = repository
        self.schema_out = schemas_out
        super().__init__(repository=self.repository, schema_out=self.schema_out)

    async def create_offices_from_json(json_data: str | dict[str, Any]) -> list[OfficeRead]:
        if isinstance(json_data, str):
            with open(json_data, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = json_data
        
        offices = []
        for office in data.get("offices", []):
            offices.append(OfficesOrm(**office))
        
        return offices


offices_service: OfficesService = OfficesService(repository=offices_repo)
