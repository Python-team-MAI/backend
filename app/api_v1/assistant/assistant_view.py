# routes/snapshots.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api_v1.assistant.models import KnowledgeSnapshotsOrm
from app.api_v1.assistant.schemas import KnowledgeSnapshotRead, KnowledgeSnapshotCreate, KnowledgeSnapshotFilter, KnowledgeSnapshotUpdate, NewSnapshotRequest
from app.core.session_manager import SessionDep, TransactionSessionDep
from app.api_v1.assistant.service import snapshots_service, yandex_service
from app.api_v1.assistant.minio_service import storage_manager
from app.api_v1.assistant.service import sdk
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Indexes"])

@router.get("")
def get_indexes():
    """Find and return all offices"""
    return yandex_service.get_indexes()
