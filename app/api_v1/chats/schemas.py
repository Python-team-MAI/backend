from pydantic import BaseModel, ConfigDict
from datetime import datetime


class Chat(BaseModel):
    name: str
    type: str
    office_id: int

class ChatRead(Chat):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ChatCreate(Chat):
    pass


class ChatUpdate(ChatCreate):
    name: str | None = None
    type: str | None = None


class ChatFilter(ChatCreate):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    name: str | None = None
    name: str | None = None
    type: str | None = None
    office_id: int | None = None
