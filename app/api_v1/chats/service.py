from app.api_v1.chats.repo import ChatsRepo
from app.api_v1.chats.repo import chats_repo
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class ChatsService(BaseService):
    def __init__(self, repository: ChatsRepo):
        self.repository = repository
        super().__init__(repository=self.repository)


chats_service: ChatsService = ChatsService(repository=chats_repo)