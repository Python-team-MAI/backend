from app.core.base.base_repository import BaseRepository
from app.api_v1.groups.models import GroupsOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


class GroupsRepo(BaseRepository):
    model = GroupsOrm


groups_repo: GroupsOrm = GroupsRepo()
