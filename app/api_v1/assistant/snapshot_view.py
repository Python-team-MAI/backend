# routes/snapshots.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, Depends
from celery.result import AsyncResult
from sqlalchemy.ext.asyncio import AsyncSession
from app.api_v1.assistant.models import KnowledgeSnapshotsOrm
from app.api_v1.assistant.schemas import (
    KnowledgeSnapshotRead,
    KnowledgeSnapshotCreate,
    KnowledgeSnapshotFilter,
    KnowledgeSnapshotUpdate,
    NewSnapshotRequest,
)
from app.core.session_manager import SessionDep, TransactionSessionDep
from app.api_v1.assistant.service import snapshots_service
from app.api_v1.minio.manager import storage_manager
from app.api_v1.auth.validation import require_superuser
import uuid
from app.api_v1.utils.setup_logging import setup_logging
import io
import zipfile

logger = setup_logging(__name__)

router = APIRouter(tags=["Snapshots"], dependencies=[])


@router.get("", response_model=list[KnowledgeSnapshotRead])
async def get_snapshots(
    session: AsyncSession = SessionDep,
):
    """Find and return all offices"""
    return await snapshots_service.find_all(session=session)


@router.get("/tasks/{snapshot_id}")
async def get_task_status(snapshot_id: int, session: AsyncSession = SessionDep):
    snapshot = await snapshots_service.find_one_or_none(
        session=session, filters=KnowledgeSnapshotFilter(id=snapshot_id)
    )
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    task = AsyncResult(snapshot.task_id)

    return {
        "task_id": snapshot.task_id,
        "task_status": task.status,
        "snapshot_status": snapshot.status,
        "index_id": snapshot.index_id,
    }
async def process_markdown_files(files: list[UploadFile]):
    """Обработка MD файлов с проверкой кодировки"""
    processed_files = []
    for file in files:
        content = await file.read()
        for encoding in ['utf-8', 'cp1251', 'iso-8859-1']:
            try:
                text_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Не удалось декодировать файл {file.filename}"
            )
        
        processed_file = UploadFile(
            filename=file.filename,
            file=io.BytesIO(text_content.encode('utf-8')),
            size=len(text_content)
        )
        processed_files.append(processed_file)
    
    return processed_files


@router.post("/snapshot")
async def create_snapshot(
    webhook_url: str = Form(None),
    archive: UploadFile = File(..., description="ZIP-архив с MD-файлами"),
    session: AsyncSession = TransactionSessionDep,
):
    try:
        archive_content = await archive.read()
        
        with zipfile.ZipFile(io.BytesIO(archive_content)) as zip_file:
            if not zip_file.namelist():
                raise HTTPException(status_code=400, detail="Архив пустой")
            
            extracted_files = []
            for file_info in zip_file.infolist():
                if file_info.is_dir() or not file_info.filename.lower().endswith('.md'):
                    continue
                
                with zip_file.open(file_info) as file:
                    file_content = file.read()
                    extracted_file = UploadFile(
                        filename=file_info.filename,
                        file=io.BytesIO(file_content),
                        size=file_info.file_size
                    )
                    extracted_files.append(extracted_file)
            
            processed_files = await process_markdown_files(extracted_files)
            uploaded_files = await storage_manager.upload_files(processed_files)
            snapshot = KnowledgeSnapshotCreate(document_paths=uploaded_files)
            snapshot = await snapshots_service.add(session=session, values=snapshot)
            
            return {"snapshot_id": snapshot.id}
    
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Некорректный ZIP-архив")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обработки MD-архива: {str(e)}"
        )


@router.post("/inheritance/{snapshot_id}")
async def create_snapshot(
    snapshot_id: int,
    webhook_url: str = Form(None),
    files: list[UploadFile] = File(...),
    session: AsyncSession = TransactionSessionDep,
):
    snapshot = await snapshots_service.find_one_or_none(
        session=session, filters=KnowledgeSnapshotFilter(id=snapshot_id)
    )
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    current_paths = snapshot.document_paths or []
    uploaded_files = await storage_manager.upload_files(files, current_paths)
    logger.info(f"Current: {current_paths}. Uploaded: {uploaded_files}")
    snapshot = KnowledgeSnapshotCreate(document_paths=uploaded_files)
    snapshot = await snapshots_service.add(session=session, values=snapshot)

    return {
        "snapshot_id": snapshot.id,
        "old_files_count": len(current_paths),
        "new_files_count": len(uploaded_files) - len(current_paths),
    }


@router.patch("/upload-file/{snapshot_id}")
async def create_snapshot(
    snapshot_id: int,
    webhook_url: str = Form(None),
    files: list[UploadFile] = File(...),
    session: AsyncSession = TransactionSessionDep,
):

    snapshot = await snapshots_service.find_one_or_none(
        session=session, filters=KnowledgeSnapshotFilter(id=snapshot_id)
    )
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    current_paths = snapshot.document_paths or []

    uploaded_files = await storage_manager.upload_files(
        files, snapshot_files=current_paths
    )
    logger.info(f"Current: {current_paths}. Uploaded: {uploaded_files}")
    await snapshots_service.update(
        session=session,
        filters=KnowledgeSnapshotFilter(id=snapshot_id),
        values=KnowledgeSnapshotUpdate(document_paths=uploaded_files),
    )

    return {
        "snapshot_id": snapshot.id,
        "new_files_count": len(uploaded_files) - len(current_paths),
    }


@router.delete("/{snapshot_id}")
async def delete_snapshot(
    snapshot_id: int,
    session: AsyncSession = TransactionSessionDep,
) -> int:
    return await snapshots_service.delete(
        session=session, filters=KnowledgeSnapshotFilter(id=snapshot_id)
    )
