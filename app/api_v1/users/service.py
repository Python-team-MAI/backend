from app.api_v1.users.repo import UsersRepo
from app.api_v1.users.repo import users_repo
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class UsersService(BaseService):
    def __init__(self, repository: UsersRepo):
        self.repository = repository
        super().__init__(repository=self.repository)


    async def is_admin(self, session: AsyncSession, user_id: int):
        await self.repository.is_admin(session=session, user_id=user_id)
    
    async def get_all_admins(self, session: AsyncSession):
        await self.repository.get_all_admins(session=session)


users_service: UsersService = UsersService(repository=users_repo)