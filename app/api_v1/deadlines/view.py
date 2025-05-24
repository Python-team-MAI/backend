from fastapi import APIRouter, HTTPException, status, Depends
from app.core.session_manager import SessionDep, TransactionSessionDep
from .schemas import DeadlineCreate, DeadlineRead, DeadlineFilter, DeadlineUpdate
from .service import deadlines_service
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import deadline_by_id
from app.api_v1.auth.validation import require_condition


router = APIRouter(
    tags=["Deadlines"],
    dependencies=[Depends(require_condition(required_role="headman"))],
)


@router.get("", response_model=list[DeadlineRead])
async def get_deadlines(
    session: AsyncSession = SessionDep,
):
    return await deadlines_service.find_all(session=session)


@router.post("", response_model=DeadlineRead, status_code=status.HTTP_201_CREATED)
async def create_deadlines(
    deadlines_in: DeadlineCreate,
    session: AsyncSession = TransactionSessionDep,
):
    return await deadlines_service.add(session=session, values=deadlines_in)


@router.get("/{deadlines_id}", response_model=DeadlineRead)
async def get_chat(deadlines=Depends(deadline_by_id)):
    return deadlines


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
