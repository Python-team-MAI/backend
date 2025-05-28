# app/tasks/index_tasks.py
from app.api_v1.celery.service import celery_app
import shutil
from app.api_v1.minio.manager import storage_manager
from app.api_v1.assistant.service import yandex_service
from app.api_v1.assistant.service import snapshots_service
from app.api_v1.assistant.schemas import KnowledgeSnapshotFilter, KnowledgeSnapshotRead
from app.core.session_manager import session_manager
import pandas as pd
import asyncio
from app.api_v1.utils.setup_logging import setup_logging


logger = setup_logging(__name__)


async def run(snapshot):
    snapshot = KnowledgeSnapshotRead(**snapshot)
    snapshot_id = snapshot.id
    async for session in session_manager.get_db():

        await snapshots_service.update(session=session, filters=KnowledgeSnapshotFilter(id=snapshot_id), values=KnowledgeSnapshotFilter(status="processing"))
        await session.commit()

        try:
            paths, temp_dir = await storage_manager.download_files_to_temp_dir(snapshot.document_paths)
            index_id = await yandex_service.create_new_index(paths)
            shutil.rmtree(temp_dir)

            await snapshots_service.update(session=session, filters=KnowledgeSnapshotFilter(id=snapshot_id), values=KnowledgeSnapshotFilter(status="ready", index_id=index_id)) 
            await session.commit()

        except Exception as e:
            await snapshots_service.update(session=session, filters=KnowledgeSnapshotFilter(id=snapshot_id), values=KnowledgeSnapshotFilter(status="failed"))
            await session.commit()
            raise

@celery_app.task(bind=True, name="create_yandex_index_from_snapshot")
def create_yandex_index_from_snapshot(self, snapshot):
    loop = asyncio.get_event_loop()  
    loop.run_until_complete(run(snapshot))  
    loop.close() 
