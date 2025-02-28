from sqlalchemy.ext.asyncio import AsyncSession
from core.models import MessagesOrm
from sqlalchemy.engine import Result
from sqlalchemy import select
from .schemas import MessageCreate, MessageUpdatePartial
from api_v1.auth.utils import hash_password


async def get_messages(session: AsyncSession) -> list[MessagesOrm]:
    stmt = select(MessagesOrm).order_by(MessagesOrm.id)
    result: Result = await session.execute(stmt)
    messages = result.scalars().all()
    return list(messages)


async def get_messages_by_chat(session: AsyncSession, chat_id: int) -> list[MessagesOrm]:
    stmt = select(MessagesOrm).where(MessagesOrm.chat_id == chat_id)
    result: Result = await session.execute(stmt)
    messages = result.scalars().all()
    return list(messages)

async def get_messages_by_user(session: AsyncSession, user_id: int) -> list[MessagesOrm]:
    stmt = select(MessagesOrm).where(MessagesOrm.user_id == user_id)
    result: Result = await session.execute(stmt)
    messages = result.scalars().all()
    return list(messages)


async def get_message_by_id(session: AsyncSession, message_id: int) -> MessagesOrm | None:
    return await session.get(MessagesOrm, message_id)


async def create_message(session: AsyncSession, message_in: MessageCreate) -> MessagesOrm:
    message = MessagesOrm(**message_in.model_dump())
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def update_Message(
    session: AsyncSession,
    message: MessagesOrm,
    message_update: MessageUpdatePartial,
    partial: bool = False,
) -> MessagesOrm:
    for name, value in message_update.model_dump(exclude_unset=partial).items():
        setattr(message, name, value)
    await session.commit()
    return message


async def delete_message(session: AsyncSession, message: MessagesOrm) -> None:
    await session.delete(message)
    await session.commit()
