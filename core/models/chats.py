from core.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .messages import MessagesOrm
    from .users import UsersOrm


class ChatType(enum.Enum):
    default = "default"


class ChatsOrm(Base):
    __tablename__ = "chats"

    name: Mapped[str] = mapped_column(String(50))
    type: Mapped[str]
    institute: Mapped[int]
    office_id: Mapped[int]

    messages: Mapped[list["MessagesOrm"]] = relationship(back_populates="chat")

    users: Mapped[list["UsersOrm"]] = relationship(back_populates="chat")