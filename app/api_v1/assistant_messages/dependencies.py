from fastapi import Depends, HTTPException, status, Path
from typing import Annotated
from app.api_v1.assistant_messages.models import AssistantMessagesOrm
from sqlalchemy.ext.asyncio import AsyncSession
from .service import assistant_messages_service
from .schemas import AssistantMessageFilter
from app.core.session_manager import SessionDep


async def assistant_message_by_id(
    assistant_message_id: Annotated[int, Path],
    session: AsyncSession = SessionDep,
) -> AssistantMessagesOrm:
    message = await assistant_messages_service.find_one_or_none(
        session=session, filters=AssistantMessageFilter(id=assistant_message_id)
    )
    if message is not None:
        return message

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Message {assistant_message_id} not found"
    )
