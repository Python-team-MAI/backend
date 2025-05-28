from app.api_v1.assistant_chats.repo import AssistantChatsRepo
from app.api_v1.assistant_chats.repo import assistant_chats_repo
from app.api_v1.assistant_chats.schemas import AssistantChatRead
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class AssistantChatsService(BaseService):
    def __init__(self, repository: AssistantChatsRepo, schemas_out=AssistantChatRead):
        self.repository = repository
        self.schema_out = AssistantChatRead
        super().__init__(repository=self.repository, schema_out=AssistantChatRead)


assistant_chats_service: AssistantChatsService = AssistantChatsService(repository=assistant_chats_repo)
