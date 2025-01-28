from sqlalchemy.ext.asyncio import AsyncSession
from core.models import ChatsOrm
from sqlalchemy.engine import Result
from sqlalchemy import select
from .schemas import ChatCreate


async def get_chats(session: AsyncSession) -> list[ChatsOrm]:
    stmt = select(ChatsOrm).order_by(ChatsOrm.id)
    result: Result = await session.execute(stmt)
    chats = result.scalars().all()
    return list(chats)


async def get_chat(session: AsyncSession, chat_id: int) -> ChatsOrm | None:
    return await session.get(ChatsOrm, chat_id)


async def create_chat(session: AsyncSession, chat_in: ChatCreate) -> ChatsOrm:
    chat = ChatsOrm(**chat_in.model_dump())
    session.add(chat)
    await session.commit()
    await session.refresh(chat)
    return chat