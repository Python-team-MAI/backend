from fastapi import APIRouter, HTTPException, status, Depends
import logging
from . import crud
from .schemas import UserCreate, UserRead, UserUpdate
from core.helpers import db_helper
from api_v1.auth.demo_jwt_auth import get_current_auth_user
from api_v1.auth.validation import require_role
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import user_by_id, user_by_email


router = APIRouter(tags=["Users"], dependencies=[Depends(get_current_auth_user), Depends(require_role("admin"))])


@router.get("", response_model=list[UserRead])
async def get_users(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_users(session=session)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_user(session=session, user_in=user_in)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user=Depends(user_by_id),
):
    return user

@router.get("/{user_email}", response_model=UserRead)
async def get_user(
    user=Depends(user_by_email),
):
    return user

@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_update: UserUpdate,
    user=Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await crud.update_user(session=session, user=user, user_update=user_update)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_update: UserUpdate,
    user=Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await crud.update_user(
        session=session, user=user, user_update=user_update, partial=True
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user: UserRead = Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> None:
    await crud.delete_user(user=user, session=session)
