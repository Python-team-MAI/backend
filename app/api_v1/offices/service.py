from app.api_v1.offices.repo import OfficesRepo
from app.api_v1.offices.repo import offices_repo
from app.api_v1.offices.schemas import OfficeRead, OfficeCreate
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
import json
from fastapi import UploadFile, HTTPException
from typing import Any
from app.api_v1.utils.setup_logging import setup_logging

logger = setup_logging(__name__)


class OfficesService(BaseService):
    def __init__(self, repository: OfficesRepo, schemas_out=OfficeRead):
        self.repository = repository
        self.schema_out = schemas_out
        super().__init__(repository=self.repository, schema_out=self.schema_out)

    async def create_offices_from_json(
        self, data, session: AsyncSession
    ) -> list[OfficeRead]:
        if "offices" not in data or not isinstance(data["offices"], list):
            raise HTTPException(
                status_code=400, detail="Invalid data format: missing 'offices' list"
            )

        ans = []
        for office_data in data["offices"]:
            try:
                office = OfficeCreate(**office_data)

                added_office = await self.add(session=session, values=office)
                ans.append(added_office)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid office data: {e}")
        return ans

    async def create_floor(self, floor: int, session: AsyncSession):
        pass


offices_service: OfficesService = OfficesService(repository=offices_repo)
