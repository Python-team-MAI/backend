from fastapi import Depends, HTTPException, status, Path
from typing import Annotated
from app.api_v1.messages.models import MessagesOrm
from sqlalchemy.ext.asyncio import AsyncSession
from .service import messages_service
from .schemas import MessageFilter
from app.core.session_manager import SessionDep


async def message_by_id(
    message_id: Annotated[int, Path],
    session: AsyncSession = SessionDep,
) -> MessagesOrm:
    message = await messages_service.find_one_or_none(session=session, filters=MessageFilter(id=message_id))
    if message is not None:
        return message

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Message {message_id} not found"
    )


