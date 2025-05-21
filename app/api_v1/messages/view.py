from fastapi import APIRouter, HTTPException, status, Depends
import logging
from .service import messages_service
from .schemas import MessageCreate, MessageRead, MessageUpdate
from app.api_v1.auth.validation import require_role, get_current_auth_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session_manager import SessionDep, TransactionSessionDep
from .dependencies import message_by_id


router = APIRouter(tags=["Messages"], dependencies=[Depends(get_current_auth_user)])


@router.get("", response_model=list[MessageRead])
async def get_messages(
    session: AsyncSession = SessionDep,
):
    """Find and return all messages"""
    return await messages_service.find_all(session=session)


@router.post("", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_in: MessageCreate,
    session: AsyncSession = TransactionSessionDep,
):
    """Create new message and return created message object"""
    return await messages_service.add(session=session, values=message_in)


@router.get("/{message_id}", response_model=MessageRead)
async def get_message(
    message=Depends(message_by_id),
):
    """Find and return message by id"""
    return message


@router.patch("/{message_id}", response_model=MessageRead)
async def update_message(
    message_update: MessageUpdate,
    message=Depends(message_by_id),
    session: AsyncSession = TransactionSessionDep,
):
    return await messages_service.update(session=session, filters=message, values=message_update)


@router.delete("/{message_id}")
async def delete_message(
    message: MessageRead = Depends(message_by_id),
    session: AsyncSession = TransactionSessionDep,
) -> int:
    return await messages_service.delete(session=session, filters=message)
