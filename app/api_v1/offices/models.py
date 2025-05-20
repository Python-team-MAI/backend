from app.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey, Boolean

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api_v1.chats.models import ChatsOrm


class OfficesOrm(Base):
    __tablename__ = "offices"
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    
    chat: Mapped["ChatsOrm"] = relationship("ChatsOrm", back_populates="office")