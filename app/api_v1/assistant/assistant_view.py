# routes/snapshots.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api_v1.assistant.models import KnowledgeSnapshotsOrm
from app.api_v1.assistant.schemas import KnowledgeSnapshotRead, KnowledgeSnapshotCreate, KnowledgeSnapshotFilter, KnowledgeSnapshotUpdate, NewSnapshotRequest
from app.core.session_manager import SessionDep, TransactionSessionDep
from app.api_v1.assistant.service import snapshots_service, yandex_service
from app.api_v1.minio.manager import storage_manager
from app.api_v1.assistant.service import sdk
from app.api_v1.auth.validation import require_superuser
import uuid
from app.api_v1.utils.setup_logging import setup_logging
logger = setup_logging(__name__)

router = APIRouter(tags=["Assistant"], dependencies=[Depends(require_superuser())])

@router.get("/indexes")
def get_indexes():
    """Find and return all offices"""
    return yandex_service.get_indexes()


@router.get("/indexes/status/task/{task_id}")
def get_status():
    """Find and return all offices"""
    


@router.post("/indexes")
async def start_index_creation(snapshot_id: int, session: AsyncSession = TransactionSessionDep):
    snapshot = await snapshots_service.find_one_or_none(
        session=session, filters=KnowledgeSnapshotFilter(id=snapshot_id)
    )
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    from app.api_v1.assistant.tasks import create_yandex_index_from_snapshot

    task = create_yandex_index_from_snapshot.delay(snapshot.model_dump(mode="json"))

    return {"task_id": task.id}
