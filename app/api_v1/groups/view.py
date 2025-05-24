from fastapi import APIRouter, HTTPException, status, Depends
from app.core.session_manager import SessionDep, TransactionSessionDep
from .schemas import GroupCreate, GroupRead, GroupFilter, GroupUpdate
from .service import groups_service
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import group_by_id
from app.api_v1.auth.validation import require_role


router = APIRouter(tags=["Groups"], dependencies=[Depends(require_role("admin"))])


@router.get("", response_model=list[GroupRead])
async def get_groups(
    session: AsyncSession = SessionDep,
):
    return await groups_service.find_all(session=session)


@router.post("", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_in: GroupCreate,
    session: AsyncSession = TransactionSessionDep,
):
    return await groups_service.add(session=session, values=group_in)


@router.get("/{group_id}", response_model=GroupRead)
async def get_groups(group=Depends(group_by_id)):
    return group


@router.patch("/{group_id}", response_model=GroupRead)
async def update_group(
    group_update: GroupUpdate,
    group=Depends(group_by_id),
    session: AsyncSession = TransactionSessionDep,
):
    return await groups_service.update(
        session=session, filters=group, values=group_update
    )


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    session: AsyncSession = TransactionSessionDep,
) -> None:
    await groups_service.delete(session=session, filters=GroupFilter(id=group_id))
