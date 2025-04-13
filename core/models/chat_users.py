# from core.models import Base
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# import enum
# from sqlalchemy import String
# from typing import TYPE_CHECKING


# if TYPE_CHECKING:
#     from .messages import MessagesOrm
#     from .users import UsersOrm


# class ChatType(enum.Enum):
#     default = "default"


# class UsersChatsOrm(Base):
#     __tablename__ = "users_chats"
    
#     user_id: Mapped[int]
#     chat_id: Mapped[int] 