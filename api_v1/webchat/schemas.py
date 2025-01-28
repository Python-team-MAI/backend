from pydantic import BaseModel, EmailStr
from datetime import datetime



class UserBase(BaseModel):
    first_name: str 
    last_name: str
    bio: str
    email: EmailStr
    password: str
    course: int
    group_id: int
    institute: int
    role: str
    # json_settings: str

class User(UserBase):
    id: int

class UserCreate(UserBase):
    pass

class GroupBase(BaseModel):
    name: str

class Group(GroupBase):
    id: int

class GroupCreate(GroupBase):
    pass

class MessageBase(BaseModel):

    text: str
    created_at: datetime
    updated_at: datetime
    chat_id: int
    user_id: int
    is_deleted: bool
    is_anonyumus: bool

class Message(MessageBase):
    id: int

class MessageCreate(MessageBase):
    pass


class ChatBase(BaseModel):

    name: str
    type: str
    institute: int
    # office_id: Mapped[int]

class Chat(ChatBase):
    id: int

class ChatCreate(ChatBase):
    id: int
