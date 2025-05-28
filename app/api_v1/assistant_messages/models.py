from app.core.base.base_model import Base
from app.api_v1.users.mixins import UsersRelationMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api_v1.assistant_chats.models import AssistantChatsOrm


class AssistantMessagesOrm(UsersRelationMixin, Base):
    __tablename__ = "assistant_messages"
    _user_back_populates = "assistant_messages"
    text: Mapped[str]
    type: Mapped[str] = mapped_column(nullable=False)
    assistant_chat_id: Mapped[int] = mapped_column(ForeignKey("assistant_chats.id", ondelete="CASCADE"))
    assistant_chat: Mapped["AssistantChatsOrm"] = relationship(back_populates="messages")
