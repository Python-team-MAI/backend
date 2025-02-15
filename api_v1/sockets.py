import socketio
from api_v1.messages.schemas import Message

# mgr = socketio.AsyncRedisManager('redis://')
sio_server = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins=[]
)

sio_app = socketio.ASGIApp(socketio_server=sio_server, socketio_path="sockets")


@sio_server.event
async def connect(sid, environ, auth):
    # print(auth)
    user_id = auth.get("user_id")
    chat_id = auth.get("chat_id")
    if not user_id or not chat_id:
        await sio_server.disconnect(sid)
        return
    await sio_server.save_session(sid, {"user_id": user_id, "chat_id": chat_id})
    # print(f"{sid}: connected as User#{user_id} in Chat#{chat_id}")
    await sio_server.enter_room(sid=sid, room=chat_id)
    await sio_server.emit(
        "join", {"sid": sid, "user_id": user_id, "chat_id": chat_id}, room=chat_id
    )


@sio_server.event
async def chat(sid, message: Message):
    chat_id = message["chat_id"]
    await sio_server.emit("chat", {"sid": sid, "message": message}, room=chat_id)


@sio_server.event
async def disconnect(sid, reason):
    # Получаем данные из сессии сокета
    session = await sio_server.get_session(sid)
    user_id = session.get("user_id")
    chat_id = session.get("chat_id")

    if user_id and chat_id:
        print(f"User#{user_id} вышел из Chat#{chat_id} (причина: {reason})")
        await sio_server.emit(
            "left", {"sid": sid, "user_id": user_id, "chat_id": chat_id}, room=chat_id
        )
        await sio_server.leave_room(sid=sid, room=chat_id)
    else:
        print(f"{sid}: disconnected without user_id or chat_id (причина: {reason})")
