from pydantic import BaseModel, EmailStr, ConfigDict
import enum
from datetime import datetime


class Message(BaseModel):
    text: str
    chat_id: int
    # media_id: Mapped[int]
    user_id: int
    is_deleted: bool = False
    is_anonymous: bool = False


class MessageRead(Message):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime
    id: int


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
