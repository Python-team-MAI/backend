from app.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api_v1.chats.models import ChatsOrm


class MessagesOrm(Base):
    __tablename__ = "messages"

    text: Mapped[str] = mapped_column(String(256))
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))
    # media_id: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    is_deleted: Mapped[bool] = mapped_column(default=False)
    is_anonymous: Mapped[bool] = mapped_column(default=False)

    chat: Mapped["ChatsOrm"] = relationship(back_populates="messages")