from fastapi import Depends, HTTPException, status, Path, Query
from typing import Annotated
from app.api_v1.chats.models import ChatsOrm
from sqlalchemy.ext.asyncio import AsyncSession
from .service import assistant_chats_service
from .schemas import AssistantChatFilter
from app.core.session_manager import SessionDep
import logging

logger = logging.getLogger(__name__)


async def assistant_chat_by_id(
    assistant_chat_id: Annotated[int, Path],
    session: AsyncSession = SessionDep,
) -> ChatsOrm:
    logger.info(f"Chat id {assistant_chat_id}")
    chat = await assistant_chats_service.find_one_or_none(
        session=session, filters=AssistantChatFilter(id=assistant_chat_id)
    )
    if chat is not None:
        return chat

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Chat {assistant_chat_id} not found"
    )
