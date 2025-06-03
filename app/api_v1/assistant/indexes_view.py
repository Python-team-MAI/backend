# routes/snapshots.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api_v1.assistant.models import KnowledgeSnapshotsOrm
from app.api_v1.assistant.schemas import (
    KnowledgeSnapshotRead,
    KnowledgeSnapshotCreate,
    MessageQuestion,
    KnowledgeSnapshotFilter,
    KnowledgeSnapshotUpdate,
    NewSnapshotRequest,
)
from app.core.session_manager import SessionDep, TransactionSessionDep
from app.api_v1.assistant.service import (
    snapshots_service,
    yandex_service,
    Agent,
    instruction as main_instruction,
)
from app.api_v1.users.service import users_service
from app.api_v1.assistant_messages.service import assistant_messages_service
from app.api_v1.assistant_chats.service import assistant_chats_service
from app.api_v1.users.schemas import UserFilter, UserUpdate, UserRead
from app.api_v1.auth.validation import get_current_auth_user
from app.api_v1.assistant_chats.schemas import (
    AssistantChatFilter,
    AssistantChatRead,
    AssistantChatCreate,
)
from app.api_v1.assistant_messages.schemas import (
    AssistantMessageCreate,
    AssistantMessageFilter,
    AssistantMessageRead,
)
from app.api_v1.minio.manager import storage_manager
from app.api_v1.auth.validation import require_superuser
import uuid
from app.api_v1.utils.setup_logging import setup_logging

logger = setup_logging(__name__)

router = APIRouter(tags=["Indexes"], dependencies=[])


@router.get("")
async def get_indexes():
    """Find and return all offices"""
    return await yandex_service.get_indexes()


@router.get("/{index_id}")
async def get_indexes(index_id: str):
    """Find and return all offices"""
    return await yandex_service.get_current_index(index_id=index_id)


@router.get("/status/task/{task_id}")
async def get_status():
    """Find and return all offices"""
    pass


@router.post("")
async def start_index_creation(
    snapshot_id: int, session: AsyncSession = TransactionSessionDep
):
    snapshot = await snapshots_service.find_one_or_none(
        session=session, filters=KnowledgeSnapshotFilter(id=snapshot_id)
    )
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    indexes = await yandex_service.get_indexes()
    if len(indexes) > 1:
        raise HTTPException(status_code=404, detail="Index already exist")
    from app.api_v1.assistant.tasks import create_yandex_index_from_snapshot

    task = create_yandex_index_from_snapshot.delay(snapshot.model_dump(mode="json"))

    return {"task_id": task.id}


@router.delete("/files")
async def delete_index():
    res = await yandex_service.delete_files()
    return res

@router.delete("/{index_id}")
async def delete_index(index_id: str):
    index = await yandex_service.get_current_index(index_id=index_id)
    try:
        await index.delete()
        return {"message": "success"}
    except Exception as ex:
        raise HTTPException(status_code=400, detail="Something wrong")
    

