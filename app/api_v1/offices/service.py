from app.api_v1.offices.repo import OfficesRepo, NodesRepo
from app.api_v1.offices.repo import offices_repo, nodes_repo
from app.api_v1.offices.schemas import OfficeRead, OfficeCreate, NodeCreate, NodeRead
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

    async def create_offices_or_nodes_from_json(self, data, session: AsyncSession) -> list[OfficeRead]:

        logger.debug(f"TYPE OF JSON DATA: {type(data["offices"])}")
        logger.debug(f"DATA: {data["offices"]}")
        if "offices" not in data or not isinstance(data["offices"], list) and "nodes" not in data or not isinstance(data["offices"], list):
            raise HTTPException(status_code=400, detail="Invalid data format: missing 'offices' list")


        ans = []
        if "offices" in data:
            for office_data in data["offices"]:
                logger.debug(f"office data: {office_data}")
                try:
                    office = OfficeCreate(**office_data)
            
                    added_office = await self.add(session=session, values=office)
                    ans.append(added_office)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Invalid office data: {e}")
        else:
            for nodes_data in data["offices"]:
                try:
                    node = NodeCreate(**nodes_data) 
            
                    added_node = await self.add(session=session, values=node)
                    ans.append(added_node)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Invalid office data: {e}")
        return ans
    


class NodesService(BaseService):
    def __init__(self, repository: NodesRepo, schemas_out=NodeRead):
        self.repository = repository
        self.schema_out = schemas_out
        super().__init__(repository=self.repository, schema_out=self.schema_out)

    async def add(self, session, values: NodeCreate):
        if values.type in ["elevator", "stairs"]:
            with open("statis/all_vertical_connections.json", "r") as f:
                content = f.read()
                data = json.loads(content)
                for connection in data:
                    if connection["type"] == values.type:
                        connection["nodes"].append(values.pid_name)
                json.dump(data, f)

        return await super().add(session, values)



offices_service: OfficesService = OfficesService(repository=offices_repo)
nodes_service: NodesService = NodesService(repository=nodes_repo)