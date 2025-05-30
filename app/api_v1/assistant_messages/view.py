from fastapi import APIRouter, HTTPException, status, Depends
import logging
from .service import assistant_messages_service
from .schemas import (
    AssistantMessageCreate,
    AssistantMessageRead,
    AssistantMessageUpdate,
)
from app.api_v1.auth.validation import require_role, get_current_auth_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session_manager import SessionDep, TransactionSessionDep
from .dependencies import assistant_message_by_id


router = APIRouter(
    tags=["AssistantMessages"], dependencies=[Depends(get_current_auth_user)]
)


@router.get("", response_model=list[AssistantMessageRead])
async def get_assistant_messages(
    session: AsyncSession = SessionDep,
):
    """Find and return all assistant_messages"""
    return await assistant_messages_service.find_all(session=session)


@router.post(
    "", response_model=AssistantMessageRead, status_code=status.HTTP_201_CREATED
)
async def create_assistant_message(
    assistant_message_in: AssistantMessageCreate,
    session: AsyncSession = TransactionSessionDep,
):
    """Create new assistant_message and return created assistant_message object"""
    return await assistant_messages_service.add(
        session=session, values=assistant_message_in
    )


@router.get("/{assistant_message_id}", response_model=AssistantMessageRead)
async def get_assistant_message(
    assistant_message=Depends(assistant_message_by_id),
):
    """Find and return assistant_message by id"""
    return assistant_message


@router.patch("/{assistant_message_id}", response_model=AssistantMessageRead)
async def update_assistant_message(
    assistant_message_update: AssistantMessageUpdate,
    assistant_message=Depends(assistant_message_by_id),
    session: AsyncSession = TransactionSessionDep,
):
    return await assistant_messages_service.update(
        session=session, filters=assistant_message, values=assistant_message_update
    )


@router.delete("/{assistant_message_id}")
async def delete_assistant_message(
    assistant_message: AssistantMessageRead = Depends(assistant_message_by_id),
    session: AsyncSession = TransactionSessionDep,
) -> int:
    return await assistant_messages_service.delete(
        session=session, filters=assistant_message
    )
