from core.models import Base, created_at, updated_at
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .users import UsersOrm


class MessagesOrm(Base):
    __tablename__ = "messages"

    text: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))
    # media_id: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    is_deleted: Mapped[bool]
    is_anonymous: Mapped[bool]

    user: Mapped["UsersOrm"] = relationship(back_populates="messages")
