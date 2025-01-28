from fastapi import APIRouter, HTTPException, status, Depends
import logging
from ..websockets import manager
from . import crud
from .schemas import ChatCreate, Chat
from core.models import db_helper
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(tags=["Chats"])


@router.get("/", response_model=list[Chat])
async def get_chats(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await crud.get_chats(session=session)


@router.post("/", response_model=Chat)
async def create_chat(
    chat_in: ChatCreate,
    session: AsyncSession = Depends(db_helper.session_dependency), 
):
    return await crud.create_chat(session=session, chat_in=chat_in)


@router.get("/{chat_id}/", response_model=Chat)
async def get_chats(
    chat_id: int, 
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    chat = await crud.get_chat(session=session, chat_id=chat_id)
    if chat is not None:
        return chat
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Chat {chat_id} not found"
    )
