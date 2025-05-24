# routes/snapshots.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api_v1.assistant.models import KnowledgeSnapshotsOrm
from app.api_v1.assistant.schemas import KnowledgeSnapshotRead, KnowledgeSnapshotCreate, KnowledgeSnapshotFilter, KnowledgeSnapshotUpdate, NewSnapshotRequest
from app.core.session_manager import SessionDep, TransactionSessionDep
from app.api_v1.assistant.service import snapshots_service
from app.api_v1.assistant.minio_service import storage_manager
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Snapshots"])

@router.get("", response_model=list[KnowledgeSnapshotRead])
async def get_snapshots(
    session: AsyncSession = SessionDep,
):
    """Find and return all offices"""
    return await snapshots_service.find_all(session=session)

@router.post("/snapshot")
async def create_snapshot(
    new_snapshot_request: NewSnapshotRequest,
    session: AsyncSession = TransactionSessionDep
):
    uploaded_files = await storage_manager.upload_files(new_snapshot_request.files)
    # Создаем запись о снапшоте
    snapshot = KnowledgeSnapshotCreate(document_paths=uploaded_files)
    snapshot = await snapshots_service.add(session=session, values=snapshot)

    return {"snapshot_id": snapshot.id}

@router.post("/inheritance/{snapshot_id}")
async def create_snapshot(
    new_snapshot_request: NewSnapshotRequest,
    session: AsyncSession = TransactionSessionDep
):
    snapshot = await snapshots_service.find_one_or_none(session=session, filters=KnowledgeSnapshotFilter(id=new_snapshot_request.id))
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    current_paths = snapshot.document_paths or []
    uploaded_files = await storage_manager.upload_files(new_snapshot_request.files, current_paths)
    # Создаем запись о снапшоте
    logger.info(f"Current: {current_paths}. Uploaded: {uploaded_files}")
    snapshot = KnowledgeSnapshotCreate(document_paths=uploaded_files)
    snapshot = await snapshots_service.add(session=session, values=snapshot)

    return {"snapshot_id": snapshot.id, "old_files_count": len(current_paths), "new_files_count": len(uploaded_files) - len(current_paths)}

@router.patch("/upload-file/{snapshot_id}")
async def create_snapshot(
    new_snapshot_request: NewSnapshotRequest,
    session: AsyncSession = TransactionSessionDep
):

    snapshot = await snapshots_service.find_one_or_none(session=session, filters=KnowledgeSnapshotFilter(id=new_snapshot_request.snapshot_id))
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    current_paths = snapshot.document_paths or []
    
    uploaded_files = await storage_manager.upload_files(new_snapshot_request.files, snapshot_files=current_paths)
    logger.info(f"Current: {current_paths}. Uploaded: {uploaded_files}")
    await snapshots_service.update(session=session, filters=KnowledgeSnapshotFilter(id=new_snapshot_request.snapshot_id), values=KnowledgeSnapshotUpdate(document_paths=uploaded_files))
    
    return {"snapshot_id": snapshot.id, "new_files_count": len(uploaded_files) - len(current_paths)}


@router.delete("/{snapshot_id}")
async def delete_snapshot(
    snapshot_id: int,
    session: AsyncSession = TransactionSessionDep,
) -> int:
    return await snapshots_service.delete(session=session, filters=KnowledgeSnapshotFilter(id=snapshot_id))
