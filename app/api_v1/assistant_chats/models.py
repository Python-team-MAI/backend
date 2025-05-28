from app.core.base.base_model import Base
from app.api_v1.users.mixins import UsersRelationMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from app.api_v1.assistant_messages.models import AssistantMessagesOrm


class AssistantChatsOrm(UsersRelationMixin, Base):
    __tablename__ = "assistant_chats"

    name: Mapped[str] = mapped_column(String(50), nullable=True)

    messages: Mapped[list["AssistantMessagesOrm"]] = relationship(back_populates="assistant_chat")
