from app.api_v1.groups.repo import GroupsRepo
from app.api_v1.groups.repo import groups_repo
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class GroupsService(BaseService):
    def __init__(self, repository: GroupsRepo):
        self.repository = repository
        super().__init__(repository=self.repository)


groups_service: GroupsService = GroupsService(repository=groups_repo)