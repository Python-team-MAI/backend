from app.core.base.base_repository import BaseRepository
from app.api_v1.messages.models import MessagesOrm
from app.api_v1.messages.schemas import MessageCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload


class MessagesRepo(BaseRepository):
    model = MessagesOrm

    async def get_sorted_messages(
        self, session: AsyncSession, chat_id: int, offset: int, limit: int
    ) -> list[MessagesOrm]:
        stmt = (
            select(MessagesOrm)
            .options(selectinload(MessagesOrm.user))
            .where(MessagesOrm.chat_id == chat_id)
            .order_by(MessagesOrm.created_at)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def add_return_user(
        self, session: AsyncSession, values: MessageCreate
    ) -> MessagesOrm:
        new_message = await self.add(session=session, values=values)

        stmt = (
            select(MessagesOrm)
            .options(selectinload(MessagesOrm.user))
            .where(MessagesOrm.id == new_message.id)
        )
        result = await session.execute(stmt)
        return result.scalar_one()


messages_repo: MessagesOrm = MessagesRepo()
