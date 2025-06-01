from fastapi import APIRouter, HTTPException, status, Depends, Request
from app.core.session_manager import SessionDep, TransactionSessionDep
from .schemas import (
    PersonalDeadlineCreate,
    GroupDeadlineCreate,
    DeadlineRead,
    DeadlineFilter,
    DeadlineUpdate,
    parse_datetime,
)
from .service import deadlines_service
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import (
    deadline_by_id,
    deadline_by_datetime_from,
    deadline_by_datetime_to,
    deadline_by_group_id,
    deadlines_by_author_id,
)
from app.api_v1.auth.validation import require_condition, get_current_auth_user, get_current_user_id
import logging

logger = logging.getLogger(__name__)


router = APIRouter(
    tags=["Deadlines"],
    dependencies=[Depends(get_current_auth_user)],
)


@router.get("", response_model=list[DeadlineRead])
async def get_deadlines(
    session: AsyncSession = SessionDep,
):
    return await deadlines_service.find_all(session=session)

@router.get("/me", response_model=list[DeadlineRead])
async def get_me_deadlines(
    user_id = Depends(get_current_user_id), 
    session: AsyncSession = SessionDep,
):

    return await deadlines_service.find_all(session=session, filters=DeadlineFilter(author_id=user_id))


@router.get("/{deadline_id}", response_model=DeadlineRead)
async def get_deadlines_by_author_id(deadline=Depends(deadline_by_id)):
    return deadline


@router.get("/user/{user_id}", response_model=list[DeadlineRead])
async def get_deadlines_by_author_id(deadlines=Depends(deadlines_by_author_id)):
    return deadlines


@router.get("/{datetime_id}", response_model=DeadlineRead)
async def get_chat(deadlines=Depends(deadline_by_id)):
    return deadlines


@router.get("/date-from/{user_id}", response_model=list[DeadlineRead])
async def get_chat(deadlines=Depends(deadline_by_datetime_from)):
    return deadlines


@router.get("/date-to/{user_id}", response_model=list[DeadlineRead])
async def get_chat(deadlines=Depends(deadline_by_datetime_to)):
    return deadlines


@router.get("/group/{group_id}", response_model=list[DeadlineRead])
async def get_chat(deadlines=Depends(deadline_by_group_id)):
    return deadlines


@router.post(
    "/personal", response_model=DeadlineRead, status_code=status.HTTP_201_CREATED
)
async def create_deadlines(
    deadlines_in: PersonalDeadlineCreate,
    session: AsyncSession = TransactionSessionDep,
):
    deadlines_in.date_from = deadlines_in.date_from.replace(tzinfo=None)
    deadlines_in.date_to = deadlines_in.date_to.replace(tzinfo=None)
    return await deadlines_service.add(session=session, values=deadlines_in)


@router.post(
    "/group",
    response_model=DeadlineRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_condition(required_role="headman"))],
)
async def create_deadlines(
    deadlines_in: GroupDeadlineCreate,
    session: AsyncSession = TransactionSessionDep,
):
    deadlines_in.date_from = deadlines_in.date_from.replace(tzinfo=None)
    deadlines_in.date_to = deadlines_in.date_to.replace(tzinfo=None)
    return await deadlines_service.add(session=session, values=deadlines_in)


@router.patch("/{deadlines_id}", response_model=DeadlineRead)
async def update_deadlines(
    deadlines_update: DeadlineUpdate,
    deadlines=Depends(deadline_by_id),
    session: AsyncSession = TransactionSessionDep,
):
    return await deadlines_service.update(
        session=session, filters=deadlines, values=deadlines_update
    )


@router.delete("/{deadlines_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deadlines(
    deadlines_id: int,
    session: AsyncSession = TransactionSessionDep,
) -> None:
    await deadlines_service.delete(
        session=session, filters=DeadlineFilter(id=deadlines_id)
    )
