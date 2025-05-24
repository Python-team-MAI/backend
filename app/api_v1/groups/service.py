from app.api_v1.groups.repo import GroupsRepo
from app.api_v1.groups.repo import groups_repo
from app.api_v1.groups.schemas import GroupRead
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class GroupsService(BaseService):
    def __init__(self, repository: GroupsRepo, schemas_out=GroupRead):
        self.repository = repository
        self.schema_out = schemas_out
        super().__init__(repository=self.repository, schema_out=schemas_out)


groups_service: GroupsService = GroupsService(repository=groups_repo)
