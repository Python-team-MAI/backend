from fastapi import APIRouter, HTTPException, status, Depends
from app.core.session_manager import SessionDep
from .schemas import ChatCreate, Chat, ChatFilter, ChatUpdate
from .service import chats_service
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import chat_by_id


router = APIRouter(tags=["Chats"])


@router.get("/", response_model=list[Chat])
async def get_chats(
    session: AsyncSession = SessionDep,
):
    return await chats_service.find_all(session=session)


@router.post("/", response_model=Chat, status_code=status.HTTP_201_CREATED)
async def create_chats(
    chats_in: ChatCreate,
    session: AsyncSession = SessionDep,
):
    return await chats_service.add(session=session, values=chats_in)


@router.get("/{chats_id}", response_model=Chat)
async def get_chat(
    chats = Depends(chat_by_id)
):
    return chats



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
