from app.api_v1.messages.repo import MessagesRepo
from app.api_v1.messages.repo import messages_repo
from app.api_v1.messages.schemas import MessageRead, MessageAndUser, MessageCreate, SocketMessageAndUser
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class MessagesService(BaseService):
    def __init__(self, repository: MessagesRepo, schemas_out=MessageRead):
        self.repository: MessagesRepo = repository
        self.schema_out = schemas_out
        super().__init__(repository=self.repository, schema_out=self.schema_out)

    async def get_sorted_messages(self, session, chat_id, offset, limit) -> list[MessageAndUser]:
        messages_orm = await self.repository.get_sorted_messages(
            session=session, chat_id=chat_id, offset=offset, limit=limit
        )
        messages = [MessageAndUser.model_validate(message) for message in messages_orm]
        return messages
    
    async def add_return_user(self, session: AsyncSession, values: MessageCreate):
        message = await self.repository.add_return_user(session=session, values=values)
        message = SocketMessageAndUser(id=message.id,
            created_at=message.created_at,
            updated_at=message.updated_at,
            first_name=message.user.first_name,  # теперь это работает
            last_name=message.user.last_name,
            text=message.text,
            user_id=message.user_id,
            chat_id=message.chat_id,
            is_anonymous=message.is_anonymous,
            user=message.user
        )
        return message



messages_service: MessagesService = MessagesService(repository=messages_repo)
