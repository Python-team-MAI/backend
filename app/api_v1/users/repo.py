from app.core.base.base_repository import BaseRepository
from app.api_v1.users.models import UsersOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

class UsersRepo(BaseRepository):
    model = UsersOrm

    async def is_admin(self, session: AsyncSession, user_id: int):
        query = select(UsersOrm).where(UsersOrm.id == user_id)
        result = await session.execute(query)
        result = result.scalar_one_or_none()
        if result:
            return result.is_superuser
        return False
    
    async def get_all_admins(self, session: AsyncSession):
        query = select(UsersOrm).where(UsersOrm.is_superuser == True)
        result = await session.execute(query)
        result = result.scalars()
        if result:
            return result
        return []


users_repo: UsersOrm = UsersRepo()