from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from app.core.session_manager import SessionDep
from app.api_v1.messages.models import MessagesOrm
from .schemas import ChatCreate, Chat, ChatFilter, ChatUpdate
from app.api_v1.messages.schemas import MessageRead
from .service import chats_service
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import chat_by_id
from app.api_v1.messages.service import messages_service
from typing import Annotated


router = APIRouter(tags=["Chats"])

PAGE_SIZE = 100

@router.get("", response_model=list[Chat])
async def get_chats(
    session: AsyncSession = SessionDep,
):
    return await chats_service.find_all(session=session)


@router.get("/{chats_id}", response_model=Chat)
async def get_chat(
    chat = Depends(chat_by_id)
):
    return chat

@router.get("/{chat_id}/messages", response_model=list[MessageRead])
async def list_chat_messages(
    chat_id: Annotated[int, Path],
    chat = Depends(chat_by_id),
    page: int = Query(1, ge=1),
    session: AsyncSession = SessionDep,
):
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    
    limit = PAGE_SIZE
    offset = (page - 1) * PAGE_SIZE
    messages = await messages_service.get_sorted_messages(session=session, chat_id=chat_id, offset=offset, limit=limit)
    return messages
    
    

@router.post("", response_model=Chat, status_code=status.HTTP_201_CREATED)
async def create_chats(
    chats_in: ChatCreate,
    session: AsyncSession = SessionDep,
):
    return await chats_service.add(session=session, values=chats_in)





@router.patch("/{chats_id}", response_model=Chat)
async def update_chats(
    chats_update: ChatFilter,
    chats=Depends(chat_by_id),
    session: AsyncSession = SessionDep,
):
    return await chats_service.update(
        session=session, filters=chats, values=chats_update
    )


@router.delete("/{chats_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chats(
    chats_id: int, 
    session: AsyncSession = SessionDep,
) -> None:
    await chats_service.delete(session=session, filters=ChatFilter(id=chats_id))


