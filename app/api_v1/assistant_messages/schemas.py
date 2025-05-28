from pydantic import BaseModel, EmailStr, ConfigDict
import enum
from datetime import datetime


class AssistantMessage(BaseModel):
    text: str
    type: str
    assistant_chat_id: int
    user_id: int


class AssistantMessageRead(AssistantMessage):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime
    id: int


class AssistantMessageCreate(AssistantMessage):
    pass


class AssistantMessageUpdate(AssistantMessageCreate):
    pass


class AssistantMessageFilter(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    text: str | None = None
    type: str | None = None
    assistant_chat_id: int | None = None
    user_id: int | None = None
