from pydantic import BaseModel
from app.api_v1.users.schemas import UserRead
from datetime import datetime


class MessageOut(BaseModel):
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
