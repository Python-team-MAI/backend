from app.api_v1.messages.repo import MessagesRepo
from app.api_v1.messages.repo import messages_repo
from app.api_v1.messages.schemas import MessageRead
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class MessagesService(BaseService):
    def __init__(self, repository: MessagesRepo, schemas_out=MessageRead):
        self.repository: MessagesRepo = repository
        self.schema_out = schemas_out
        super().__init__(repository=self.repository, schema_out=self.schema_out)

    async def get_sorted_messages(self, session, chat_id, offset, limit):
        return await self.repository.get_sorted_messages(
            session=session, chat_id=chat_id, offset=offset, limit=limit
        )


messages_service: MessagesService = MessagesService(repository=messages_repo)
