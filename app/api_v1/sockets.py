import socketio
from app.api_v1.messages.schemas import MessageCreate
from app.api_v1.messages.service import messages_service
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session_manager import SessionDep, session_manager
from fastapi import Depends
import logging

logger = logging.getLogger(__name__)

sio_server = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins=[]
)

sio_app = socketio.ASGIApp(socketio_server=sio_server)


@sio_server.event
async def connect(sid, environ, auth):
    logger.info(f"New sid {sid} connected. Auth: {auth}")
    user_id = auth.get("user_id")
    chat_id = auth.get("chat_id")
    if not user_id or not chat_id:
        await sio_server.disconnect(sid)
        return
    await sio_server.save_session(sid, {"user_id": user_id, "chat_id": chat_id})

    await sio_server.enter_room(sid=sid, room=chat_id)
    await sio_server.emit(
        "join", {"sid": sid, "user_id": user_id, "chat_id": chat_id}, room=chat_id
    )
    
@sio_server.event
@session_manager.connection(commit=True)
async def chat(sid, message, session):
    logger.info(f"Sid: {sid}. New message received: {message}")
    chat_id = message["chat_id"]
    await sio_server.emit("chat", {"sid": sid, "message": message}, room=chat_id)

    message  = MessageCreate(text=message["text"], user_id=message["user_id"], chat_id=message["chat_id"], is_anonymous=message["is_anonymous"])
    await messages_service.add(session=session, values=message)


@sio_server.event
async def disconnect(sid, reason):
    logger.info(f"Sid {sid} disconnected. Reason: {reason}")
    session = await sio_server.get_session(sid)
    user_id = session.get("user_id")
    chat_id = session.get("chat_id")

    if user_id and chat_id:
        await sio_server.emit(
            "left", {"sid": sid, "user_id": user_id, "chat_id": chat_id}, room=chat_id
        )
        await sio_server.leave_room(sid=sid, room=chat_id)
    else:
        logger.info(f"{sid}: disconnected without user_id or chat_id (причина: {reason})")
