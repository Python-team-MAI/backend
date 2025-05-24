from fastapi import APIRouter, HTTPException, status, Depends
import logging
from .service import offices_service
from .schemas import OfficeCreate, OfficeRead, OfficeUpdate
from app.api_v1.auth.validation import require_role, require_superuser
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session_manager import SessionDep, TransactionSessionDep
from .dependencies import office_by_id


router = APIRouter(tags=["Offices"], dependencies=[Depends(require_superuser)])


@router.get("", response_model=list[OfficeRead])
async def get_offices(
    session: AsyncSession = SessionDep,
):
    """Find and return all offices"""
    return await offices_service.find_all(session=session)


@router.post("", response_model=OfficeRead, status_code=status.HTTP_201_CREATED)
async def create_office(
    office_in: OfficeCreate,
    session: AsyncSession = TransactionSessionDep,
):
    """Create new office and return created office object"""
    return await offices_service.add(session=session, values=office_in)


@router.get("/{office_id}", response_model=OfficeRead)
async def get_office(
    office=Depends(office_by_id),
):
    """Find and return office by id"""
    return office


@router.patch("/{office_id}", response_model=OfficeRead)
async def update_office(
    office_update: OfficeUpdate,
    office=Depends(office_by_id),
    session: AsyncSession = TransactionSessionDep,
):
    return await offices_service.update(
        session=session, filters=office, values=office_update
    )


@router.delete("/{office_id}")
async def delete_office(
    office: OfficeRead = Depends(office_by_id),
    session: AsyncSession = TransactionSessionDep,
) -> int:
    return await offices_service.delete(session=session, filters=office)
