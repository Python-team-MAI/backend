from fastapi import Depends, HTTPException, status, Path
from typing import Annotated
from app.api_v1.chats.models import ChatsOrm
from sqlalchemy.ext.asyncio import AsyncSession
from .service import chats_service
from .schemas import ChatsFilter
from app.core.session_manager import SessionDep


async def chats_by_id(
    chats_id: Annotated[int, Path],
    session: AsyncSession = SessionDep,
) -> ChatsOrm:
    chats = await chats_service.find_one_or_none(session=session, filters=ChatsFilter(id=chats_id))
    if chats is not None:
        return chats

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Chat {chats_id} not found"
    )


