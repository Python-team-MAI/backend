from app.core.base.base_repository import BaseRepository
from app.api_v1.assistant_messages.models import AssistantMessagesOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


class AssistantMessagesRepo(BaseRepository):
    model = AssistantMessagesOrm

    async def get_sorted_messages(
        self, session: AsyncSession, chat_id: int, offset: int, limit: int
    ) -> list[AssistantMessagesOrm]:
        stmt = (
            select(AssistantMessagesOrm)
            .where(AssistantMessagesOrm.assistant_chat_id == chat_id)
            .order_by(AssistantMessagesOrm.created_at)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_message_with_user_info():
        pass


assistant_messages_repo: AssistantMessagesRepo = AssistantMessagesRepo()
