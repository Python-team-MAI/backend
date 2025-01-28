from pydantic import BaseModel, ConfigDict
from datetime import datetime

class MessageBase(BaseModel):

    text: str
    created_at: datetime
    updated_at: datetime
    chat_id: int
    user_id: int
    is_deleted: bool
    is_anonyumus: bool

class Message(MessageBase):
    model_config  = ConfigDict(from_attributes=True)

    id: int

class MessageCreate(MessageBase):
    pass


class ChatBase(BaseModel):

    name: str
    type: str
    institute: int
    # office_id: Mapped[int]

class Chat(ChatBase):
    model_config  = ConfigDict(from_attributes=True)

    id: int

class ChatCreate(ChatBase):
    pass
