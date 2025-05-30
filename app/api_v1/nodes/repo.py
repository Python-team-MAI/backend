from app.core.base.base_repository import BaseRepository
from app.api_v1.nodes.models import NodesOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


class NodesRepo(BaseRepository):
    model = NodesOrm


nodes_repo: NodesRepo = NodesRepo()
