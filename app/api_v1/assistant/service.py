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
from yandex_cloud_ml_sdk import AsyncYCloudML
from fastapi import HTTPException, status
from app.core.config import settings
from uuid import uuid4
import pandas as pd
import os
import asyncio
from app.api_v1.utils.setup_logging import setup_logging

logger = setup_logging(__name__)


class YandexService:
    def __init__(self):
        self.sdk = AsyncYCloudML(
            auth=settings.assistant.YANDEX_CLOUD_API_KEY,
            folder_id=settings.assistant.YANDEX_CLOUD_FOLDER_ID,
        )
        self.model = self.sdk.models.completions("yandexgpt", model_version="rc")
        self.folder_id = settings.assistant.YANDEX_CLOUD_FOLDER_ID

    async def create_thread(self):
        thread = await self.sdk.threads.create(ttl_days=3, expiration_policy="static")
        logger.debug(f"Created thread: {thread}")
        return thread

    async def create_assistant(self, model, tools=None):
        logger.debug("Start creating assistant...")
        kwargs = {}
        if tools and len(tools) > 0:
            kwargs = {"tools": tools}
        assistant = await self.sdk.assistants.create(
            model, ttl_days=3, expiration_policy="since_last_active", **kwargs
        )
        logger.debug(f"End creating assistant: {assistant}")
        return assistant

    async def get_token_count(self, text):
        res = await self.model.tokenize(text)
        return len(res)

    async def get_token_count(self, filename):
        with open(filename, "r") as f:
            res = await self.model.tokenize(f.read())
            return len(res)

    def get_file_len(self, filename):
        with open(filename) as f:
            l = len(f.read())
        return l

    def upload_file(self, directory_path):
        return self.sdk.files.upload(
            directory_path, ttl_days=3, expiration_policy="static"
        )

    async def create_new_index(self, document_paths: list[str]) -> str:
        """
        Создаёт новый индекс и добавляет в него документы.
        Возвращает ID созданного индекса.
        """
        uploaded_files = (self.upload_file(path) for path in document_paths)
        files = await asyncio.gather(*uploaded_files)
        operation = await self.sdk.search_indexes.create_deferred(
            files,
            index_type=HybridSearchIndexType(
                chunking_strategy=StaticIndexChunkingStrategy(
                    max_chunk_size_tokens=700,
                    chunk_overlap_tokens=300,
                )
            ),
        ttl_days=2,
        expiration_policy="since_last_active"
        )
        search_index = await operation
        logger.info(f"Создали индекс: {search_index}")

        return search_index.id

    async def get_current_index(self, index_id: str):
        """Получаем индекс по айди"""
        return await self.sdk.search_indexes.get(search_index_id=index_id)

    async def get_first_index(self):
        indexes = await self.get_indexes()
        if not indexes:
            raise HTTPException(status_code=400, detail="Indexes not found")
        return yandex_service.sdk.tools.search_index(indexes[0])

    async def get_indexes(self) -> list:
        indexes = []
        try:
            async for index in self.sdk.search_indexes.list():
                logger.info(f"Find index with id: {index.id}")
                if index:
                    indexes.append(index.id)
        except Exception as ex:
            logger.error(f"Произошла ошибка при получении индекса: {ex}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex)

        return indexes

    async def get_assistants(self) -> list:
        assistants = []
        try:
            async for index in self.sdk.assistants.list():
                logger.debug(f"Assistant: {assistants}")
                if index:
                    assistants.append(index.id)
        except Exception as ex:
            logger.error(f"Произошла ошибка при получении индекса: {ex}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex)

        return assistants

    async def get_assistant(self, assistant_id: str):
        """Возвращает ассистента по его ID"""
        return await self.sdk.assistants.get(assistant_id=assistant_id)

    def get_instruction(self):
        with open("instruction2.md", "r", encoding="utf-8") as f:
            instruction = f.read()
        return instruction
    
    async def delete_files(self):
        try:
            res = 0
            async for file in self.sdk.files.list():
                await file.delete()
                res += 1
                logger.info(f"Delete {file.name}")
            return res
        except Exception as e:
            logger.error(f"Exception: {e}")


    def update_index(self, index_id: str, document_paths: list[str]):
        pass


yandex_service: YandexService = YandexService()
instruction = yandex_service.get_instruction()


class Agent:

    @classmethod
    async def create(
        cls,
        thread_id=None,
        assistant=None,
        instruction=None,
        search_index=None,
        tools=None,
    ):
        self = cls()
        self.thread_id = thread_id
        self.thread = None

        if assistant:
            self.assistant = assistant
        else:
            if tools:
                self.tools = {x.__name__: x for x in tools}
                tools = [yandex_service.sdk.tools.function(x) for x in tools]
            else:
                self.tools = {}
                tools = []
            if search_index:
                index = await yandex_service.sdk.tools.search_index(search_index)
                tools.append(index)
            self.assistant = await yandex_service.create_assistant(
                yandex_service.model, tools
            )

        if instruction:
            await self.assistant.update(instruction=instruction)
        return self

    async def get_thread(self, thread=None):
        if self.thread_id is not None:
            logger.info(f"thread_id: {self.thread_id}")
            self.thread = await yandex_service.sdk.threads.get(self.thread_id)
            logger.info(f"existing thread: {self.thread}")
            return self.thread
        if self.thread_id == None:
            self.thread = await yandex_service.create_thread()
            logger.info(f"created thread: {self.thread}")
        return self.thread

    async def __call__(self, message, thread=None):
        thread = await self.get_thread(thread)
        await thread.write(message)
        run = await self.assistant.run(thread)
        res = await run
        logger.info(f"Result: {res}")
        return res.text, self.thread.id

    async def restart(self):
        if self.thread:
            await self.thread.delete()
            self.thread = await yandex_service.sdk.threads.create(
                name="Test", ttl_days=1, expiration_policy="static"
            )

    async def done(self, delete_assistant=False):
        if self.thread:
            await self.thread.delete()
        if delete_assistant:
            await self.assistant.delete()


class KnowledgeSnapshotsService(BaseService):
    def __init__(
        self, repository: KnowledgeSnapshotsRepo, schemas_out=KnowledgeSnapshotRead
    ):
        self.repository = repository
        self.schema_out = KnowledgeSnapshotRead
        super().__init__(repository=self.repository, schema_out=KnowledgeSnapshotRead)


snapshots_service: KnowledgeSnapshotsService = KnowledgeSnapshotsService(
    repository=snapshots_repo, schemas_out=KnowledgeSnapshotRead
)
