from app.api_v1.assistant_messages.repo import AssistantMessagesRepo
from app.api_v1.assistant_messages.repo import assistant_messages_repo
from app.api_v1.assistant_messages.schemas import AssistantMessageRead
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class AssistantMessagesService(BaseService):
    def __init__(
        self, repository: AssistantMessagesRepo, schemas_out=AssistantMessageRead
    ):
        self.repository: AssistantMessagesRepo = repository
        self.schema_out = schemas_out
        super().__init__(repository=self.repository, schema_out=self.schema_out)

    async def get_sorted_assistant_messages(self, session, chat_id, offset, limit):
        return await self.repository.get_sorted_messages(
            session=session, chat_id=chat_id, offset=offset, limit=limit
        )


assistant_messages_service: AssistantMessagesService = AssistantMessagesService(
    repository=assistant_messages_repo
)
