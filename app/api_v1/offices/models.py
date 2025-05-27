from app.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey, Boolean, Integer, ARRAY

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api_v1.chats.models import ChatsOrm


class OfficesOrm(Base):
    __tablename__ = "offices"
    desc: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=False)
    color: Mapped[str] = mapped_column(nullable=False)
    length: Mapped[int] = mapped_column(nullable=False)
    width: Mapped[int] = mapped_column(nullable=False)
    height: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    coords: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)

    chat: Mapped["ChatsOrm"] = relationship("ChatsOrm", back_populates="office")

