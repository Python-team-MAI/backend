from fastapi import APIRouter, HTTPException, status, Depends
from app.core.session_manager import SessionDep
from .schemas import ChatsCreate, Chats, ChatsFilter, ChatsUpdate
from .service import chats_service
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import chats_by_id


router = APIRouter(tags=["Chatss"])


@router.get("/", response_model=list[Chats])
async def get_chats(
    session: AsyncSession = SessionDep,
):
    return await chats_service.find_all(session=session)


@router.post("/", response_model=Chats, status_code=status.HTTP_201_CREATED)
async def create_chats(
    chats_in: ChatsCreate,
    session: AsyncSession = SessionDep,
):
    return await chats_service.add(session=session, values=chats_in)


@router.get("/{chats_id}", response_model=Chats)
async def get_chat(
    chats = Depends(chats_by_id)
):
    return chats



@router.patch("/{chats_id}", response_model=Chats)
async def update_chats(
    chats_update: ChatsFilter,
    chats=Depends(chats_by_id),
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
    await chats_service.delete(session=session, filters=ChatsFilter(id=chats_id))
