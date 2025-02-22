from fastapi import APIRouter, HTTPException, status, Depends
from . import crud
from .schemas import GroupCreate, Group, GroupUpdatePartial, GroupUpdate
from core.helpers import db_helper
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import group_by_id


router = APIRouter(tags=["Groups"])


@router.get("/", response_model=list[Group])
async def get_groups(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await crud.get_groups(session=session)


@router.post("/", response_model=Group, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_in: GroupCreate,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await crud.create_group(session=session, group_in=group_in)


@router.get("/{group_id}/", response_model=Group)
async def get_groups(
    group_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    group = await crud.get_group(session=session, group_id=group_id)
    if group is not None:
        return group

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Group {group_id} not found"
    )


@router.put("/{group_id}/", response_model=Group)
async def update_group(
    group_update: GroupUpdate,
    group=Depends(group_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await crud.update_group(
        session=session, group=group, group_update=group_update
    )


@router.patch("/{group_id}/", response_model=Group)
async def update_group(
    group_update: GroupUpdatePartial,
    group=Depends(group_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await crud.update_group(
        session=session, group=group, group_update=group_update, partial=True
    )


@router.delete("/{group_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group: Group = Depends(group_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> None:
    await crud.delete_group(group=group, session=session)
