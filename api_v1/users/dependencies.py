from fastapi import Depends, HTTPException, status, Path
from typing import Annotated
from core.models import db_helper, UsersOrm
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud


async def user_by_id(
    user_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> UsersOrm:
    user = await crud.get_user(session=session, user_id=user_id)
    if user is not None:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found"
    )
