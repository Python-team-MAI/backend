from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from app.core.session_manager import SessionDep, TransactionSessionDep
from app.api_v1.messages.models import MessagesOrm
from app.api_v1.users.schemas import UserRead
from .schemas import (
    AssistantChatCreate,
    AssistantChatRead,
    AssistantChatFilter,
    AssistantChatUpdate,
)
from app.api_v1.assistant_messages.schemas import (
    AssistantMessageRead,
    AssistantMessageFilter,
)
from .service import assistant_chats_service
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import assistant_chat_by_id
from app.api_v1.assistant_messages.service import assistant_messages_service
from app.api_v1.auth.validation import (
    require_role,
    require_condition,
    get_current_auth_user,
    require_superuser,get_current_user_id
)
from typing import Annotated
import logging


router = APIRouter(tags=["AssistantChats"], dependencies=[Depends(get_current_auth_user)])
logger = logging.getLogger(__name__)
PAGE_SIZE = 100


@router.get(
    "",
    response_model=list[AssistantChatRead],
    dependencies=[Depends(require_superuser)],
)
async def get_assistant_chats(
    session: AsyncSession = SessionDep,
):
    return await assistant_chats_service.find_all(session=session)


@router.get("/me", response_model=list[AssistantChatRead])
async def get_assistant_chats(
    user_id: str = Depends(lambda request: request.state.user_id),
    session: AsyncSession = SessionDep
):
    return await assistant_chats_service.find_all(
        session=session, filters=AssistantChatFilter(user_id=user_id)
    )


@router.get("/messages/me", response_model=list[AssistantMessageRead])
async def get_assistant_chats(
    user_id = Depends(get_current_user_id), session: AsyncSession = SessionDep
):
    return await assistant_messages_service.find_all(
        session=session, filters=AssistantMessageFilter(user_id=user_id)
    )


@router.get(
    "/{assistant_chat_id}",
    response_model=AssistantChatRead,
    dependencies=[Depends(require_superuser)],
)
async def get_assistant_chat(assistant_chat=Depends(assistant_chat_by_id)):
    return assistant_chat


@router.get("/{assistant_chat_id}/messages", response_model=list[AssistantMessageRead])
async def list_assistant_chat_messages(
    assistant_chat_id: Annotated[int, Path],
    assistant_chat=Depends(assistant_chat_by_id),
    page: int = Query(1, ge=1),
    session: AsyncSession = SessionDep,
):
    if not assistant_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AssistantChat not found"
        )

    limit = PAGE_SIZE
    offset = (page - 1) * PAGE_SIZE
    messages = await assistant_messages_service.get_sorted_assistant_messages(
        session=session, chat_id=assistant_chat_id, offset=offset, limit=limit
    )
    return messages


@router.post("", response_model=AssistantChatRead, status_code=status.HTTP_201_CREATED)
async def create_assistant_chats(
    assistant_chats_in: AssistantChatCreate,
    session: AsyncSession = TransactionSessionDep,
):
    return await assistant_chats_service.add(session=session, values=assistant_chats_in)


@router.patch("/{assistant_chats_id}", response_model=AssistantChatRead)
async def update_assistant_chats(
    assistant_chats_update: AssistantChatUpdate,
    assistant_chats=Depends(assistant_chat_by_id),
    session: AsyncSession = TransactionSessionDep,
):
    return await assistant_chats_service.update(
        session=session, filters=assistant_chats, values=assistant_chats_update
    )


@router.delete("/{assistant_chats_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assistant_chats(
    assistant_chats_id: int,
    session: AsyncSession = TransactionSessionDep,
) -> None:
    await assistant_chats_service.delete(
        session=session, filters=AssistantChatFilter(id=assistant_chats_id)
    )
