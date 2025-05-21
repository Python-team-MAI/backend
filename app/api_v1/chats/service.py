from app.api_v1.chats.repo import ChatsRepo
from app.api_v1.chats.repo import chats_repo
from app.api_v1.chats.schemas import ChatRead
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class ChatsService(BaseService):
    def __init__(self, repository: ChatsRepo, schemas_out = ChatRead):
        self.repository = repository
        self.schema_out = ChatRead
        super().__init__(repository=self.repository, schema_out=ChatRead)


chats_service: ChatsService = ChatsService(repository=chats_repo)