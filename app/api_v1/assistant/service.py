from app.api_v1.assistant.repo import KnowledgeSnapshotsRepo
from app.api_v1.assistant.repo import snapshots_repo
from app.api_v1.assistant.schemas import KnowledgeSnapshotRead
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from app.api_v1.utils.setup_logging import setup_logging
from yandex_cloud_ml_sdk.search_indexes import (
    StaticIndexChunkingStrategy,
    HybridSearchIndexType,
    ReciprocalRankFusionIndexCombinationStrategy,
    
)
from yandex_cloud_ml_sdk import YCloudML
from app.core.config import settings
from uuid import uuid4
import os
import logging

sdk = YCloudML(auth=settings.assistant.YANDEX_CLOUD_API_KEY,  folder_id=settings)
model = sdk.models.completions("yandexgpt", model_version="rc")
logger = logging.getLogger(__name__)


def create_thread():
    logger.debug("Start creating thread...")
    thread = sdk.threads.create(ttl_days=1, expiration_policy="static")
    logger.debug(f"End creating thread: {thread}")

def create_assistant(model, tools=None):
    logger.debug("Start creating assistant...")
    kwargs = {}
    if tools and len(tools) > 0:
        kwargs = {"tools": tools}
    assistant = sdk.assistants.create(
        model, ttl_days=1, expiration_policy="since_last_active", **kwargs
    )
    logger.debug(f"End creating assistant: {assistant}")
    return assistant

def get_token_count(text):
    return len(model.tokenize(text))

def upload_file(directory_path, indent=0):
    file = sdk.files.upload(directory_path, ttl_days=1, expiration_policy="static")
    logger.debug(f"Upload new file: {file.name}")

class Agent:
    def __init__(self, thread_id=None, assistant=None, instruction=None, search_index=None, tools=None):

        self.thread_id = thread_id
        self.thread = None

        if assistant:
            self.assistant = assistant
        else:
            if tools:
                self.tools = {x.__name__: x for x in tools}
                tools = [sdk.tools.function(x) for x in tools]
            else:
                self.tools = {}
                tools = []
            if search_index:
                tools.append(sdk.tools.search_index(search_index))
            self.assistant = create_assistant(model, tools)

        if instruction:
            self.assistant.update(instruction=instruction)

    def get_thread(self, thread=None):
        if self.thread_id is not None:
            logger.info(f"thread_id: {self.thread_id}")
            self.thread = sdk.threads.get(self.thread_id)
            logger.info(f"existing thread: {self.thread}")
            return self.thread
        if self.thread_id == None:
            self.thread = create_thread()
            logger.info(f"created thread: {self.thread}")
        return self.thread

    def __call__(self, message, thread=None):
        thread = self.get_thread(thread)
        logger.info(f"get thread: {thread}")
        thread.write(message)
        run = self.assistant.run(thread)
        res = run.wait()
        return  res.text, self.thread.id
        

    def restart(self):
        if self.thread:
            self.thread.delete()
            self.thread = sdk.threads.create(
                name="Test", ttl_days=1, expiration_policy="static"
            )

    def done(self, delete_assistant=False):
        if self.thread:
            self.thread.delete()
        if delete_assistant:
            self.assistant.delete()

class YandexIndexService:
    def __init__(self):
        self.folder_id = settings.assistant.YANDEX_CLOUD_FOLDER_ID

    def create_new_index(self, document_paths: list[str]) -> str:
        """
        Создаёт новый индекс и добавляет в него документы.
        Возвращает ID созданного индекса.
        """
        # 1. Создаем индекс
        operation = sdk.search_indexes.create_deferred(
        index_type=HybridSearchIndexType(
            chunking_strategy=StaticIndexChunkingStrategy(
                max_chunk_size_tokens=700,
                chunk_overlap_tokens=300,
            )
        ),
        )
        search_index = operation.wait()
        logger.info(f"Создали индекс: {search_index}")

        for path in document_paths:
            upload_file(path)
            
        return search_index.id

    def get_current_index(self, index_id: str):
        """Удаляет индекс по его ID"""
        return sdk.search_indexes.get(search_index_id=index_id)
    
    def update_index(self, index_id: str, document_paths: list[str]):
        pass


class KnowledgeSnapshotsService(BaseService):
    def __init__(self, repository: KnowledgeSnapshotsRepo, schemas_out=KnowledgeSnapshotRead):
        self.repository = repository
        self.schema_out = KnowledgeSnapshotRead
        super().__init__(repository=self.repository, schema_out=KnowledgeSnapshotRead)


snapshots_service: KnowledgeSnapshotsService = KnowledgeSnapshotsService(repository=snapshots_repo, schemas_out=KnowledgeSnapshotRead)
yandex_service: YandexIndexService = YandexIndexService()