from app.api_v1.users.repo import UsersRepo
from app.api_v1.users.schemas import UserRead, UserCreate, UserFilter
from app.api_v1.users.repo import users_repo
from app.api_v1.auth.utils import hash_password
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

import logging
from app.api_v1.utils.setup_logging import setup_logging
logger = setup_logging(__name__)

class UsersService(BaseService):
    def __init__(self, repository: UsersRepo, schema=UserRead):
        self.repository = repository
        self.schema_out = schema
        super().__init__(repository=self.repository, schema_out=self.schema_out)

    async def is_admin(self, session: AsyncSession, user_id: int):
        await self.repository.is_admin(session=session, user_id=user_id)

    async def get_all_admins(self, session: AsyncSession):
        await self.repository.get_all_admins(session=session)

    async def create_new_user(
        self, session: AsyncSession, email: EmailStr, password: str, auth_type: str
    ) -> UserRead:
        user_create = UserCreate(
            email=email,
            password=hash_password(password),
            auth_type="default",
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )
        user = await users_service.add(session=session, values=user_create)
        logger.info(f"Create new user: {email} Auth_type: {auth_type} ")
        return user

    async def get_user_by_email(self, session: AsyncSession, email: EmailStr):
        return await self.repository.find_one_or_none(
            session=session, filters=UserFilter(email=email)
        )

    async def get_user_by_id(self, session: AsyncSession, id: int) -> UserRead:
        return await self.repository.find_one_or_none(
            session=session, filters=UserFilter(id=id)
        )

    async def set_user_is_verify(self, session: AsyncSession, email: EmailStr):
        return await self.repository.update(
            session=session,
            filters=UserFilter(email=email),
            values=UserFilter(is_verified=True),
        )

    async def reset_user_password(
        self, session: AsyncSession, email: EmailStr, new_password
    ):
        return await self.repository.update(
            session=session,
            filters=UserFilter(email=email),
            values=UserFilter(password=hash_password(new_password)),
        )


users_service: UsersService = UsersService(repository=users_repo)
