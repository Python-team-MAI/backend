from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AssistantChat(BaseModel):
    name: str | None = None
    user_id: int


class AssistantChatRead(AssistantChat):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AssistantChatCreate(AssistantChat):
    pass


class AssistantChatUpdate(AssistantChatCreate):
    name: str | None = None


class AssistantChatFilter(AssistantChatCreate):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    name: str | None = None
    user_id: int | None = None
