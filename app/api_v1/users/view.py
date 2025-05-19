from fastapi import APIRouter, HTTPException, status, Depends
import logging
from .service import users_service
from .schemas import UserCreate, UserRead, UserUpdate
from app.api_v1.auth.demo_jwt_auth import get_current_auth_user
from app.api_v1.auth.validation import require_role
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session_manager import SessionDep, TransactionSessionDep
from .dependencies import user_by_id, user_by_email


router = APIRouter(tags=["Users"], dependencies=[Depends(get_current_auth_user), Depends(require_role("admin"))])


@router.get("", response_model=list[UserRead])
async def get_users(
    session: AsyncSession = SessionDep,
):
    """Find and return all users"""
    return await users_service.find_all(session=session)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    session: AsyncSession = SessionDep,
):
    """Create new user and return created user object"""
    return await users_service.add(session=session, values=user_in)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user=Depends(user_by_id),
):
    """Find and return user by id"""
    return user

@router.get("/{user_email}", response_model=UserRead)
async def get_user(
    user=Depends(user_by_email),
):
    """Find and return user by email"""
    return user

@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_update: UserUpdate,
    user=Depends(user_by_id),
    session: AsyncSession = SessionDep,
):
    return await users_service.update(session=session, filters=user, values=user_update)


@router.delete("/{user_id}")
async def delete_user(
    user: UserRead = Depends(user_by_id),
    session: AsyncSession = SessionDep,
) -> int:
    return await users_service.delete(session=session, filters=user)
