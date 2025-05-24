from app.core.base.base_repository import BaseRepository
from app.api_v1.chats.models import ChatsOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


class ChatsRepo(BaseRepository):
    model = ChatsOrm


chats_repo: ChatsOrm = ChatsRepo()
