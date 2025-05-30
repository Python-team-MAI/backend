from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
import logging
from .service import nodes_service
from .schemas import NodeCreate, NodeRead, NodeFilter
from app.api_v1.auth.validation import require_role, require_superuser
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session_manager import SessionDep, TransactionSessionDep

import json

router = APIRouter(tags=["Nodes"], dependencies=[Depends(require_superuser)])


@router.get("/nodes", response_model=list[NodeRead])
async def get_nodes(
    session: AsyncSession = SessionDep,
):
    """Find and return all nodes"""
    return await nodes_service.find_all(session=session)


@router.post("/nodes", response_model=NodeRead, status_code=status.HTTP_201_CREATED)
async def create_node(
    node_in: NodeCreate,
    session: AsyncSession = TransactionSessionDep,
):
    """Create new node and return created node object"""
    return await nodes_service.add(session=session, values=node_in)


@router.post("/from-json", status_code=status.HTTP_201_CREATED)
async def create_node_from_json(
    file: UploadFile = File(...),
    session: AsyncSession = TransactionSessionDep,
):
    """Create new node or nodes from json"""
    try:
        content = await file.read()
        data = json.loads(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {e}")
    return await nodes_service.create_nodes_from_json(data=data, session=session)


@router.delete("/nodes/{node_id}")
async def delete_node(
    node_id,
    session: AsyncSession = TransactionSessionDep,
) -> int:
    return await nodes_service.delete(session=session, filters=NodeFilter(id=node_id))
