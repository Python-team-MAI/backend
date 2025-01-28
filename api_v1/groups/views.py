from fastapi import APIRouter, HTTPException, status, Depends
from . import crud
from .schemas import GroupCreate, Group
from core.models import db_helper
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(tags=["Groups"])


@router.get("/", response_model=list[Group])
async def get_groups(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await crud.get_groups(session=session)


@router.post("/", response_model=Group)
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
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Group {group_id} not found"
    )
