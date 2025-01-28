from fastapi import Depends, HTTPException, status, Path
from typing import Annotated
from core.models import db_helper, GroupsOrm
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud


async def group_by_id(
    group_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> GroupsOrm:
    group = await crud.get_group(session=session, group_id=group_id)
    if group is not None:
        return group

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Group {group_id} not found"
    )
