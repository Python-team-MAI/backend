from pydantic import BaseModel, ConfigDict
from datetime import datetime


class Chats(BaseModel):
    name: str
    type: str
    office_id: int

class ChatsRead(Chats):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ChatsCreate(Chats):
    pass


class ChatsUpdate(ChatsCreate):
    pass


class ChatsFilter(ChatsCreate):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    name: str | None = None
    name: str | None = None
    type: str | None = None
    office_id: int | None = None
