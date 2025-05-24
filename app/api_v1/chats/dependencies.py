from fastapi import Depends, HTTPException, status, Path, Query
from typing import Annotated
from app.api_v1.chats.models import ChatsOrm
from sqlalchemy.ext.asyncio import AsyncSession
from .service import chats_service
from .schemas import ChatFilter
from app.core.session_manager import SessionDep
import logging

logger = logging.getLogger(__name__)


async def chat_by_id(
    chat_id: Annotated[int, Path],
    session: AsyncSession = SessionDep,
) -> ChatsOrm:
    logger.info(f"Chat id {chat_id}")
    chats = await chats_service.find_one_or_none(
        session=session, filters=ChatFilter(id=chat_id)
    )
    if chats is not None:
        return chats

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Chat {chat_id} not found"
    )
