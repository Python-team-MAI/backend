# routes/snapshots.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api_v1.assistant.models import KnowledgeSnapshotsOrm
from app.api_v1.assistant.schemas import KnowledgeSnapshotRead, KnowledgeSnapshotCreate, MessageQuestion, KnowledgeSnapshotFilter, KnowledgeSnapshotUpdate, NewSnapshotRequest
from app.core.session_manager import SessionDep, TransactionSessionDep
from app.api_v1.assistant.service import snapshots_service, yandex_service, Agent, instruction as main_instruction
from app.api_v1.users.service import users_service
from app.api_v1.assistant_messages.service import assistant_messages_service
from app.api_v1.assistant_chats.service import assistant_chats_service
from app.api_v1.users.schemas import UserFilter, UserUpdate, UserRead
from app.api_v1.auth.validation import get_current_auth_user
from app.api_v1.assistant_chats.schemas import AssistantChatFilter, AssistantChatRead, AssistantChatCreate
from app.api_v1.assistant_messages.schemas import AssistantMessageCreate, AssistantMessageFilter, AssistantMessageRead
from app.api_v1.minio.manager import storage_manager
from app.api_v1.auth.validation import require_superuser
import uuid
from app.api_v1.utils.setup_logging import setup_logging
logger = setup_logging(__name__)

router = APIRouter(tags=["Assistant"], dependencies=[])


@router.get("")
async def get_assistants():
    return await yandex_service.get_assistants()

@router.get("/{assistant_id}")
async def get_assistant(assistant_id):
    return await yandex_service.get_assistant(assistant_id=assistant_id)

@router.post("")
async def question(user: UserRead = Depends(get_current_auth_user), session: AsyncSession = TransactionSessionDep):
    if user.assistant_id:
        raise HTTPException(status_code=409, detail="This user already have assistant")
    index = await yandex_service.get_first_index()
    assistant = await yandex_service.create_assistant(model=yandex_service.model, tools=[index])
    await users_service.update(session=session, filters=UserFilter(id=user.id), values=UserUpdate(assistant_id=assistant.id))
    return {"assistant_id": assistant.id, "user_id": user.id}

@router.post("/question")
async def ask_question(message: MessageQuestion, user: UserRead = Depends(get_current_auth_user), session: AsyncSession = TransactionSessionDep):
    assistant_id = user.assistant_id
    thread_id = user.thread_id
    index = await yandex_service.get_first_index()
    if not assistant_id:
        assistant = await yandex_service.create_assistant(model=yandex_service.model, tools=[index])
        assistant_id = assistant.id
        await users_service.update(session=session, filters=UserFilter(id=user.id), values=UserUpdate(assistant_id=assistant_id))

    assistant = await yandex_service.get_assistant(assistant_id=assistant_id)
    if not thread_id:
        thread = await yandex_service.create_thread()
        logger.debug(f"Create a thread: {thread}")
        thread_id = thread.id
        await users_service.update(session=session, filters=UserFilter(id=user.id), values=UserUpdate(thread_id=thread_id))

    agent = await Agent.create(thread_id=thread_id, assistant=assistant, instruction=main_instruction, search_index=index)
    ans, thread_id = await agent(message.message)

    chat = await assistant_chats_service.find_one_or_none(session=session, filters=AssistantChatFilter(user_id=user.id))
    if not chat:
        chat = await assistant_chats_service.add(session=session, values=AssistantChatCreate(user_id=user.id))
    await assistant_messages_service.add(session=session, values=AssistantMessageCreate(text=message.message, assistant_chat_id=chat.id, user_id=user.id, type="user"))
    await assistant_messages_service.add(session=session, values=AssistantMessageCreate(text=ans, assistant_chat_id=chat.id, user_id=user.id, type="assistant"))
    return {"ans": ans, "assistant_id": assistant_id, "user_id": user.id}



@router.delete("/{assistant_id}")
async def delete_index(assistant_id: str):
    assistant = await yandex_service.get_assistant(assistant_id=assistant_id)
    try:
        await assistant.delete()
        return {"message": "success"}
    except Exception as ex:
        raise HTTPException(status_code=400, detail="Something wrong")

@router.delete("")
async def delete_index(user: UserRead = Depends(get_current_auth_user), session: AsyncSession = SessionDep):
    assistant_id = user.assistant_id
    if not assistant_id:
        raise HTTPException(status_code=404, detail="User dont have assistant")
    try:
        assistant = await yandex_service.get_assistant(assistant_id=assistant_id)
        await assistant.delete()
        return {"message": "success"}
    except Exception as ex:
        raise HTTPException(status_code=400, detail="Something wrong")


@router.get("/indexes")
async def get_indexes():
    """Find and return all offices"""
    return await yandex_service.get_indexes()


@router.get("/indexes/{index_id}")
async def get_indexes(index_id: str):
    """Find and return all offices"""
    return await yandex_service.get_current_index(index_id=index_id)

@router.get("/indexes/status/task/{task_id}")
async def get_status():
    """Find and return all offices"""
    pass

@router.post("/indexes")
async def start_index_creation(snapshot_id: int, session: AsyncSession = TransactionSessionDep):
    snapshot = await snapshots_service.find_one_or_none(
        session=session, filters=KnowledgeSnapshotFilter(id=snapshot_id)
    )
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    indexes = await yandex_service.get_indexes()
    if len(indexes) > 1:
        raise HTTPException(status_code=404, detail="Index already exist")
    from app.api_v1.assistant.tasks import create_yandex_index_from_snapshot

    task = create_yandex_index_from_snapshot.delay(snapshot.model_dump(mode="json"))

    return {"task_id": task.id}

@router.delete("/indexes/{index_id}")
async def delete_index(index_id: str):
    index = await yandex_service.get_current_index(index_id=index_id)
    try:
        await index.delete()
        return {"message": "success"}
    except Exception as ex:
        raise HTTPException(status_code=400, detail="Something wrong")
