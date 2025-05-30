from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
    File,
    UploadFile,
    Query,
    Path,
)
import logging
from app.api_v1.offices.service import offices_service
from app.api_v1.nodes.service import nodes_service
from app.api_v1.offices.schemas import (
    OfficeCreate,
    OfficeRead,
    OfficeUpdate,
    OfficeFilter,
    OfficesAndChats,
)
from app.api_v1.offices.models import OfficesOrm
from app.api_v1.nodes.schemas import NodeFilter, NodeRead
from app.api_v1.auth.validation import require_role, require_superuser
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session_manager import SessionDep, TransactionSessionDep
from app.api_v1.offices.dependencies import office_by_id
from sqlalchemy.orm import selectinload
import json
from app.api_v1.utils.setup_logging import setup_logging

logger = setup_logging(__name__)

router = APIRouter(tags=["Offices"], dependencies=[Depends(require_superuser)])


@router.get("", response_model=list[OfficeRead])
async def get_offices(
    session: AsyncSession = SessionDep,
):
    """Find and return all offices"""
    return await offices_service.find_all(session=session)


@router.post("/from-json", status_code=status.HTTP_201_CREATED)
async def create_office_from_json(
    file: UploadFile = File(...),
    session: AsyncSession = TransactionSessionDep,
):
    """Create new office or nodes from json"""
    try:
        content = await file.read()
        data = json.loads(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {e}")
    return await offices_service.create_offices_from_json(data=data, session=session)


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


@router.get("/map/floor/{floor}")
async def get_floor(
    floor: int = Path(..., description="Этаж"), session: AsyncSession = SessionDep
):
    offices_orm = await offices_service.repository.find_all_with_chat(
        session=session, filters=OfficeFilter(floor=floor)
    )
    logger.debug(f"Offices orm: {offices_orm}")
    offices = [OfficesAndChats.model_validate(office) for office in offices_orm]
    nodes = await nodes_service.find_all(
        session=session, filters=NodeFilter(floor=floor)
    )
    return {"offices": offices, "nodes": nodes}


@router.delete("/map/floor/{floor}")
async def get_floor(
    floor: int = Path(..., description="Этаж"),
    session: AsyncSession = TransactionSessionDep,
):
    offices = await offices_service.delete(
        session=session, filters=OfficeFilter(floor=floor)
    )
    nodes = await nodes_service.delete(session=session, filters=NodeFilter(floor=floor))
    return {"deleted_offices": offices, "deleted_nodes": nodes}


@router.patch("/{office_id}")
async def update_office(
    office_update: OfficeUpdate,
    office=Depends(office_by_id),
    session: AsyncSession = TransactionSessionDep,
) -> int:
    return await offices_service.update(
        session=session, filters=office, values=office_update
    )


@router.delete("/{office_id}")
async def delete_office(
    office_id: int,
    session: AsyncSession = TransactionSessionDep,
) -> int:
    return await offices_service.delete(
        session=session, filters=OfficeFilter(id=office_id)
    )
