from fastapi import APIRouter, HTTPException, status, Depends
from . import crud
from .schemas import ChatCreate, Chat, ChatUpdate, ChatUpdatePartial
from .dependencies import chat_by_id
from core.models import db_helper
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(tags=["Chats"])


@router.get("/", response_model=list[Chat])
async def get_chats(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await crud.get_chats(session=session)


@router.post("/", response_model=Chat, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_in: ChatCreate,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await crud.create_chat(session=session, chat_in=chat_in)


@router.get("/{chat_id}/", response_model=Chat)
async def get_chat(
    chat=Depends(chat_by_id),
):
    return chat


@router.put("/{chat_id}/", response_model=Chat)
async def update_chat(
    chat_update: ChatUpdate,
    chat=Depends(chat_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await crud.update_chat(session=session, chat=chat, chat_update=chat_update)


@router.patch("/{chat_id}/", response_model=Chat)
async def update_chat(
    chat_update: ChatUpdatePartial,
    chat=Depends(chat_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await crud.update_chat(
        session=session, chat=chat, chat_update=chat_update, partial=True
    )


@router.delete("/{chat_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat: Chat = Depends(chat_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> None:
    await crud.delete_chat(chat=chat, session=session)
