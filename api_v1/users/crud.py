from sqlalchemy.ext.asyncio import AsyncSession
from core.models import UsersOrm
from sqlalchemy.engine import Result
from sqlalchemy import select
from .schemas import UserCreate


async def get_users(session: AsyncSession) -> list[UsersOrm]:
    stmt = select(UsersOrm).order_by(UsersOrm.id)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)


async def get_user(session: AsyncSession, user_id: int) -> UsersOrm | None:
    return await session.get(UsersOrm, user_id)


async def create_user(session: AsyncSession, user_in: UserCreate) -> UsersOrm:
    user = UsersOrm(**user_in.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user