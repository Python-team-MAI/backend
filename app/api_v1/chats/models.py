from app.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.api_v1.messages.models import MessagesOrm
    from app.api_v1.users.models import UsersOrm


class ChatType(enum.Enum):
    office = "office"
    all = "all"


class ChatsOrm(Base):
    __tablename__ = "chats"

    name: Mapped[str] = mapped_column(String(50))
    type: Mapped[str]
    office_id: Mapped[int]
    messages: Mapped[list["MessagesOrm"]] = relationship(back_populates="chat")

    # users: Mapped[list["UsersOrm"]] = relationship(back_populates="chats")