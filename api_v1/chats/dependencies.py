from fastapi import Depends, HTTPException, status, Path
from typing import Annotated
from core.models import db_helper, ChatsOrm
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud


async def chat_by_id(
    chat_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> ChatsOrm:
    chat = await crud.get_chat(session=session, chat_id=chat_id)
    if chat is not None:
        return chat

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Chat {chat_id} not found"
    )
