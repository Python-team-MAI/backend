from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
import logging
from .service import offices_service, nodes_service
from .schemas import OfficeCreate, OfficeRead, OfficeUpdate, NodeCreate, NodeRead, NodeFilter, OfficeFilter
from app.api_v1.auth.validation import require_role, require_superuser
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session_manager import SessionDep, TransactionSessionDep
from .dependencies import office_by_id
import json

router = APIRouter(tags=["Offices"], dependencies=[Depends(require_superuser)])


@router.get("", response_model=list[OfficeRead])
async def get_offices(
    session: AsyncSession = SessionDep,
):
    """Find and return all offices"""
    return await offices_service.find_all(session=session)

@router.get("/nodes", response_model=list[NodeRead])
async def get_nodes(
    session: AsyncSession = SessionDep,
):
    """Find and return all nodes"""
    return await nodes_service.find_all(session=session)


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
    return await offices_service.create_offices_or_nodes_from_json(data=data, session=session)


@router.post("", response_model=OfficeRead, status_code=status.HTTP_201_CREATED)
async def create_office(
    office_in: OfficeCreate,
    session: AsyncSession = TransactionSessionDep,
):
    """Create new office and return created office object"""
    return await offices_service.add(session=session, values=office_in)

@router.post("/nodes", response_model=NodeRead, status_code=status.HTTP_201_CREATED)
async def create_node(
    node_in: NodeCreate,
    session: AsyncSession = TransactionSessionDep,
):
    """Create new office and return created office object"""
    return await nodes_service.add(session=session, values=node_in)


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
    office_id: int, 
    session: AsyncSession = TransactionSessionDep,
) -> int:
    return await offices_service.delete(session=session, filters=OfficeFilter(id=office_id))


@router.delete("/nodes/{node_id}")
async def delete_node(
    node_id, 
    session: AsyncSession = TransactionSessionDep,
) -> int:
    return await offices_service.delete(session=session, filters=NodeFilter(id=node_id))