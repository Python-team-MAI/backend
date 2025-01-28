from core.models import Base, idpk, created_at, updated_at
from users import UsersOrm
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
import enum

class ChatType(enum.Enum):
    default = "default"

class MessagesOrm(Base):
    __tablename__ = "messages"

    text: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))
    # media_id: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    is_deleted: Mapped[bool]
    is_anonyumus: Mapped[bool]

    user: Mapped["UsersOrm"] = relationship(
        back_populates="messages"
    )


class ChatsOrm(Base):
    __tablename__ = "chats"

    name: Mapped[str] = mapped_column(String(50))
    type: Mapped[ChatType]
    institute: Mapped[int]
    # office_id: Mapped[int]


