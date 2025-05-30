from pydantic import BaseModel, EmailStr, ConfigDict
from app.api_v1.users.schemas import UserRead
import enum
from datetime import datetime


class Message(BaseModel):
    text: str
    chat_id: int
    # media_id: Mapped[int]
    user_id: int
    is_deleted: bool = False
    is_anonymous: bool = False


class MessageAndUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    text: str
    chat_id: int
    # media_id: Mapped[int]
    user_id: int
    is_deleted: bool = False
    is_anonymous: bool = False
    user: UserRead | None


class MessageRead(Message):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime
    id: int


class SocketMessageAndUser(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    first_name: str | None
    last_name: str | None
    text: str
    chat_id: int
    user_id: int
    is_deleted: bool = False
    is_anonymous: bool = False
    user: UserRead | None


class MessageCreate(Message):
    pass


class MessageUpdate(MessageCreate):
    pass


class MessageFilter(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    text: str | None = None
    chat_id: int | None = None
    # media_id: Mapped[int]
    user_id: int | None = None
    is_deleted: bool | None = None
    is_anonymous: bool | None = None
