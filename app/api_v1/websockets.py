from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from collections import defaultdict
from app.core.session_manager import SessionDep
from app.api_v1.users.dependencies import user_by_id

router = APIRouter(prefix="/ws", tags=["Websockets"])

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = defaultdict(
            list
        )  # user_id -> [websockets]
        self.chats: dict[int, list[WebSocket]] = defaultdict(
            list
        )  # chat_id -> [websockets]

    async def connect_to_chat(self, websocket: WebSocket, user_id: int, chat_id: int):
        """Подключает WebSocket клиента, добавляет его в активные соединения и чат"""
        await websocket.accept()
        self.active_connections[user_id].append(websocket)

        if websocket not in self.chats[chat_id]:
            self.chats[chat_id].append(websocket)

        # Уведомляем всех в чате о новом участнике
        await self.send_message_in_chat(
            f"Client#{user_id} has joined the chat", chat_id, system_message=True
        )

    def disconnect(self, websocket: WebSocket, chat_id: int, user_id: int):
        """Удаляет WebSocket из списков подключений"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[
                user_id
            ]:  # Если у юзера не осталось соединений, удалить запись
                del self.active_connections[user_id]

        if chat_id in self.chats:
            self.chats[chat_id].remove(websocket)
            if not self.chats[chat_id]:  # Если в чате никого не осталось, удалить чат
                del self.chats[chat_id]

    async def send_message_in_chat(
        self,
        message: str,
        chat_id: int,
        author_id: int = None,
        system_message: bool = False,
    ):
        """Отправляет сообщение всем пользователям в чате"""
        if chat_id in self.chats:
            for connection in self.chats[chat_id]:
                try:
                    if system_message:
                        await connection.send_text(message)
                    elif connection in self.active_connections.get(author_id, []):
                        await connection.send_text(
                            f"You: {message}"
                        )  # Сообщение от себя
                    else:
                        await connection.send_text(
                            f"Client#{author_id}: {message}"
                        )  # Сообщение от другого пользователя
                except Exception:
                    logger.error(f"Ошибка отправки сообщения пользователю {connection}")


manager = ConnectionManager()


@router.websocket("/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    user_id: int,
    session: AsyncSession = SessionDep,
):
    """Основная точка входа для WebSocket-подключений"""
    user = user_by_id(user_id, session)
    await manager.connect_to_chat(websocket, user_id, chat_id)

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Client#{user_id} says: {data} in chat: {chat_id}")
            await manager.send_message_in_chat(data, chat_id, author_id=user_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id, user_id)
        await manager.send_message_in_chat(
            f"Client#{user_id} has left the chat", chat_id, system_message=True
        )
