from app.api_v1.nodes.repo import NodesRepo
from app.api_v1.nodes.repo import nodes_repo
from app.api_v1.nodes.schemas import NodeCreate, NodeRead
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
import json
from fastapi import UploadFile, HTTPException
from typing import Any
from app.api_v1.utils.setup_logging import setup_logging

logger = setup_logging(__name__)


class NodesService(BaseService):
    def __init__(self, repository: NodesRepo, schemas_out=NodeRead):
        self.repository = repository
        self.schema_out = schemas_out
        super().__init__(repository=self.repository, schema_out=self.schema_out)



    # async def add(self, session, values: NodeCreate):
    #     if values.type in ["elevator", "stairs"]:
    #         with open("static/all_vertical_connections.json", "r", encoding="utf-8") as f:
    #             content = f.read()
    #             data = json.loads(content)
    #         logger.debug(f"Node type: {values.type}")
    #         for connection in data:
    #             if connection["type"] == values.type:
    #                 connection["nodes"].append(values.pid_name)
    #         with open("static/all_vertical_connections.json", "w", encoding="utf-8") as f:
    #             json.dump(data, f)

    #     return await super().add(session, values)
    
    async def create_nodes_from_json(self, data, session: AsyncSession) -> list[NodeRead]:
        if ("nodes" not in data or not isinstance(data["nodes"], list)):
            raise HTTPException(status_code=400, detail="Invalid data format: missing 'nodes' list")


        ans = []
        for node_data in data["nodes"]:
            try:
                node = NodeCreate(**node_data)
        
                added_node = await self.add(session=session, values=node)
                ans.append(added_node)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid node data: {e}")
        return ans
    
nodes_service: NodesService = NodesService(repository=nodes_repo, schemas_out=NodeRead)