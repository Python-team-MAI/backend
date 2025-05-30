import socketio
from .schemas import MessageOut
from app.api_v1.messages.schemas import MessageCreate
from app.api_v1.messages.service import messages_service
from app.api_v1.users.service import users_service
from app.api_v1.users.schemas import UserFilter
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session_manager import SessionDep, session_manager
from fastapi import Depends
from app.api_v1.auth.utils import decode_jwt
from app.api_v1.auth.validation import validate_token, get_user_by_token_sub
from app.api_v1.auth.helpers import ACCESS_TOKEN_TOKEN_TYPE
from app.api_v1.utils.setup_logging import setup_logging
logger = setup_logging(__name__)

sio_server = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])

sio_app = socketio.ASGIApp(socketio_server=sio_server)


async def validate_socket_token(sid, session, access_token):
    res = await validate_token(token=access_token, token_type=ACCESS_TOKEN_TOKEN_TYPE)
    if not res["success"]:
        logger.warning(
            f"Connection rejected. Access token not validate. {res["error"]}"
        )
        await sio_server.disconnect(sid)
        return
    try:
        payload = decode_jwt(token=access_token)
        user = await get_user_by_token_sub(payload=payload, session=session)
    except Exception as e:
        logger.warning(f"Connection rejected: {e}")
        await sio_server.disconnect(sid)
        return

    return user

@sio_server.event
@session_manager.connection(commit=True)
async def connect(sid, environ, auth, session):
    access_token = auth.get("access_token")
    user = await validate_socket_token(sid=sid, session=session, access_token=access_token)
    user_id = user.id
    chat_id = auth.get("chat_id")
    if not chat_id:
        logger.warning(f"Connection rejected. No chat_id: {chat_id}")
        await sio_server.disconnect(sid)
        return

    await sio_server.save_session(
        sid,
        {
            "user_id": user_id,
            "chat_id": chat_id,
            "fist_name": user.first_name,
            "last_name": user.last_name,
        },
    )
    await sio_server.enter_room(sid=sid, room=chat_id)


@sio_server.event
@session_manager.connection(commit=True)
async def chat(sid, message, session):
    access_token = message.get("access_token")
    user = await validate_socket_token(sid=sid, session=session, access_token=access_token)
    user_id = user.id
    chat_id = message["chat_id"]
    socket_session = await sio_server.get_session(sid)
    message_create = MessageCreate(
        text=message["text"],
        user_id=user_id,
        chat_id=chat_id,
        is_anonymous=message["is_anonymous"],
    )
    message = await messages_service.add_return_user(session=session, values=message_create)
    await sio_server.emit(
        "chat", {"sid": sid, "message": message.model_dump(mode="json")}, room=chat_id
    )


@sio_server.event
async def disconnect(sid, reason):
    session = await sio_server.get_session(sid)
    user_id = session.get("user_id")
    chat_id = session.get("chat_id")

    if user_id and chat_id:
        await sio_server.leave_room(sid=sid, room=chat_id)
        await sio_server.disconnect(sid)
        return
    else:
        logger.warning(
            f"{sid}: disconnected without user_id or chat_id (причина: {reason})"
        )
        await sio_server.disconnect(sid)
        return
