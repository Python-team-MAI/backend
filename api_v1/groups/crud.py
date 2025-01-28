from sqlalchemy.ext.asyncio import AsyncSession
from core.models import GroupsOrm
from sqlalchemy.engine import Result
from sqlalchemy import select
from .schemas import GroupCreate


async def get_groups(session: AsyncSession) -> list[GroupsOrm]:
    stmt = select(GroupsOrm).order_by(GroupsOrm.id)
    result: Result = await session.execute(stmt)
    groups = result.scalars().all()
    return list(groups)


async def get_group(session: AsyncSession, group_id: int) -> GroupsOrm | None:
    return await session.get(GroupsOrm, group_id)


async def create_group(session: AsyncSession, group_in: GroupCreate) -> GroupsOrm:
    group = GroupsOrm(**group_in.model_dump())
    session.add(group)
    await session.commit()
    await session.refresh(group)
    return group