from fastapi import Depends, HTTPException, status, Path
from typing import Annotated
from app.api_v1.groups.models import GroupsOrm
from sqlalchemy.ext.asyncio import AsyncSession
from .service import groups_service
from .schemas import GroupFilter
from app.core.session_manager import SessionDep


async def group_by_id(
    group_id: Annotated[int, Path],
    session: AsyncSession = SessionDep,
) -> GroupsOrm:
    group = await groups_service.find_one_or_none(
        session=session, filters=GroupFilter(id=group_id)
    )
    if group is not None:
        return group

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Group {group_id} not found"
    )
