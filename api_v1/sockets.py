import socketio
from api_v1.messages.schemas import Message


sio_server = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])

sio_app = socketio.ASGIApp(socketio_server=sio_server, socketio_path="sockets")


@sio_server.event
async def connect(sid, environ, auth):
    # print(f"{sid}: connected")
    # print(f"environ: {environ}")
    # await sio_server.enter_room(sid, chat_id)
    await sio_server.emit("join", {"sid": sid})


@sio_server.event
async def chat(sid, message: Message, auth):
    await sio_server.emit("chat", {"sid": sid, "message": message})


@sio_server.event
async def disconnect(sid, environ, auth):
    print(f"{sid}: disconnected")
    await sio_server.emit("left", {"sid": sid})
