from app.api_v1.messages.repo import MessagesRepo
from app.api_v1.messages.repo import messages_repo
from app.core.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class MessagesService(BaseService):
    def __init__(self, repository: MessagesRepo):
        self.repository = repository
        super().__init__(repository=self.repository)


messages_service: MessagesService = MessagesService(repository=messages_repo)