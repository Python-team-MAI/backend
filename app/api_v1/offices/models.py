from app.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey, Boolean, Integer, ARRAY, FLOAT

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.api_v1.chats.models import ChatsOrm


class OfficesOrm(Base):
    __tablename__ = "offices"
    desc: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=False)
    color: Mapped[str] = mapped_column(nullable=False)
    length: Mapped[float] = mapped_column(FLOAT, nullable=False)
    width: Mapped[float] = mapped_column(FLOAT, nullable=False)
    height: Mapped[float] = mapped_column(FLOAT, nullable=False)
    floor: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    coords: Mapped[list[float]] = mapped_column(ARRAY(FLOAT), nullable=False)

    chat: Mapped["ChatsOrm"] = relationship("ChatsOrm", back_populates="office")

