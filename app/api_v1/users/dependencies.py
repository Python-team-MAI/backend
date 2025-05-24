from fastapi import Depends, HTTPException, status, Path
from typing import Annotated
from app.api_v1.users.models import UsersOrm
from sqlalchemy.ext.asyncio import AsyncSession
from .service import users_service
from .schemas import UserFilter, UserRead
from app.core.session_manager import SessionDep


async def user_by_id(
    user_id: Annotated[int, Path],
    session: AsyncSession = SessionDep,
) -> UserRead:
    user = await users_service.find_one_or_none(
        session=session, filters=UserFilter(id=user_id)
    )
    if user is not None:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found"
    )


async def user_by_email(
    email: Annotated[str, Path],
    session: AsyncSession = SessionDep,
) -> UserRead:
    user = await users_service.get_user_by_email(session=session, email=email)
    if user is not None:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with email {email} not found",
    )
