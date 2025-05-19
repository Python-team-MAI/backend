from fastapi import Depends, HTTPException, status, Path
from typing import Annotated
from app.api_v1.offices.models import OfficesOrm
from sqlalchemy.ext.asyncio import AsyncSession
from .service import offices_service
from .schemas import OfficeFilter
from app.core.session_manager import SessionDep


async def office_by_id(
    office_id: Annotated[int, Path],
    session: AsyncSession = SessionDep,
) -> OfficesOrm:
    office = await offices_service.find_one_or_none(session=session, filters=OfficeFilter(id=office_id))
    if office is not None:
        return office

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Office {office_id} not found"
    )


