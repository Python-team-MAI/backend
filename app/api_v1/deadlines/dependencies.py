from fastapi import Depends, HTTPException, status, Path, Body
from typing import Annotated
from app.api_v1.deadlines.models import DeadlinesOrm
from app.api_v1.deadlines.schemas import DeadlineRead
from sqlalchemy.ext.asyncio import AsyncSession
from .service import deadlines_service
from .schemas import DeadlineFilter, parse_datetime, DeadlineRead
from app.core.session_manager import SessionDep
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def deadline_by_id(
    deadline_id: Annotated[int, Path],
    session: AsyncSession = SessionDep,
) -> DeadlineRead:
    
    deadline = await deadlines_service.find_one_or_none(
        session=session, filters=DeadlineFilter(id=deadline_id)
    )
    if deadline is not None:
        return deadline

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Deadline {deadline_id} not found",
    )

async def deadlines_by_author_id(
    user_id: Annotated[int, Path],
    session: AsyncSession = SessionDep,
) -> list[DeadlineRead]:
    
    deadlines = await deadlines_service.find_all(
        session=session, filters=DeadlineFilter(author_id=user_id)
    )
    if deadlines is not None:
        return deadlines

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Author {user_id} not found",
    )


async def deadline_by_datetime_to(
    user_id: Annotated[int, Path],
    date: Annotated[datetime, Body],
    interval_seconds: Annotated[int, Body],
    session: AsyncSession = SessionDep,
) -> list[DeadlineRead]:

    date_from = parse_datetime(date)
    deadlines = await deadlines_service.get_deadline_by_date_to(session=session, date=date_from, author_id=user_id, interval_seconds=interval_seconds)
    if deadlines != []:
        return deadlines

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Deadline {date} not found",
    )


async def deadline_by_datetime_from(
    user_id: Annotated[int, Path],
    date: Annotated[datetime, Body],
    interval_seconds: Annotated[int, Body],
    session: AsyncSession = SessionDep,
) -> list[DeadlineRead]:

    date_from = parse_datetime(date)
    deadlines = await deadlines_service.get_deadline_by_date_from(session=session, date=date_from, author_id=user_id, interval_seconds=interval_seconds)
    if deadlines != []:
        return deadlines

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Deadlines with {date} and {interval_seconds} not found",
    )


async def deadline_by_group_id(
    group_id: Annotated[int, Path],
    session: AsyncSession = SessionDep,
) -> DeadlinesOrm:
    deadlines = await deadlines_service.find_all(
        session=session, filters=DeadlineFilter(group_id=group_id)
    )
    if deadlines != []:
        return deadlines

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Deadline with group id {group_id} not found",
    )