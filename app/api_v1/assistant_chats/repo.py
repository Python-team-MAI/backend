from app.core.base.base_repository import BaseRepository
from app.api_v1.assistant_chats.models import AssistantChatsOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


class AssistantChatsRepo(BaseRepository):
    model = AssistantChatsOrm


assistant_chats_repo: AssistantChatsOrm = AssistantChatsRepo()
