from sqlalchemy.ext.asyncio import AsyncSession
from core.models import UsersOrm
from sqlalchemy.engine import Result
from sqlalchemy import select
from .schemas import UserCreate, UserUpdate, UserRead
from api_v1.auth.utils import hash_password


async def get_users(session: AsyncSession) -> list[UsersOrm]:
    stmt = select(UsersOrm).order_by(UsersOrm.id)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)


async def get_user_by_id(session: AsyncSession, user_id: int) -> UsersOrm | None:
    return await session.get(UsersOrm, user_id)


async def get_user_by_email(session: AsyncSession, email: str) -> UsersOrm | None:
    query = select(UsersOrm).where(UsersOrm.email == email)
    res = await session.execute(query)

    return res.scalar()


async def create_user(session: AsyncSession, user_in: UserCreate) -> UsersOrm:
    user_in.password = hash_password(user_in.password.decode())
    user = UsersOrm(**user_in.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(
    session: AsyncSession,
    user: UsersOrm,
    user_update: UserUpdate,
    partial: bool = False,
) -> UsersOrm:
    for name, value in user_update.model_dump(exclude_unset=partial).items():
        setattr(user, name, value)
    await session.commit()
    return user


async def delete_user(session: AsyncSession, user: UsersOrm) -> None:
    await session.delete(user)
    await session.commit()
