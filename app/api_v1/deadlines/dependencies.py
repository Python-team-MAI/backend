from fastapi import Depends, HTTPException, status, Path
from typing import Annotated
from app.api_v1.deadlines.models import ChatsOrm
from sqlalchemy.ext.asyncio import AsyncSession
from .service import deadlines_service
from .schemas import DeadlineFilter
from app.core.session_manager import SessionDep


async def deadline_by_id(
    deadline_id: Annotated[int, Path],
    session: AsyncSession = SessionDep,
) -> ChatsOrm:
    deadline = await deadlines_service.find_one_or_none(session=session, filters=DeadlineFilter(id=deadline_id))
    if deadline is not None:
        return deadline

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Deadline {deadline_id} not found"
    )


