from pydantic import BaseModel, EmailStr, ConfigDict
import enum
from datetime import datetime


class MessageBase(BaseModel):
    text: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    chat_id: int
    # media_id: Mapped[int]
    user_id: int
    is_deleted: bool | None = False
    is_anonymous: bool 


class Message(MessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class MessageCreate(MessageBase):
    pass


class MessageUpdate(MessageCreate):
    pass


class MessageUpdatePartial(BaseModel):
    text: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    chat_id: int | None = None
    # media_id: Mapped[int]
    user_id: int | None = None
    is_deleted: bool | None = None
    is_anonymous: bool | None = None
