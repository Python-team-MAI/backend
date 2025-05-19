from app.core.base.base_repository import BaseRepository
from app.api_v1.messages.models import MessagesOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

class MessagesRepo(BaseRepository):
    model = MessagesOrm


messages_repo: MessagesOrm = MessagesRepo()