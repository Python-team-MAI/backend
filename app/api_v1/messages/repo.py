from app.core.base.base_repository import BaseRepository
from app.api_v1.messages.models import MessagesOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


class MessagesRepo(BaseRepository):
    model = MessagesOrm

    async def get_sorted_messages(
        self, session: AsyncSession, chat_id: int, offset: int, limit: int
    ) -> list[MessagesOrm]:
        stmt = (
            select(MessagesOrm)
            .where(MessagesOrm.chat_id == chat_id)
            .order_by(MessagesOrm.created_at)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_message_with_user_info():
        pass


messages_repo: MessagesOrm = MessagesRepo()
