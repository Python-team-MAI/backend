from app.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey, Boolean, Integer, ARRAY, FLOAT

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
    floor: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    coords: Mapped[list[float]] = mapped_column(ARRAY(FLOAT), nullable=False)

    chat: Mapped["ChatsOrm"] = relationship("ChatsOrm", back_populates="office")



class NodesOrm(Base):
    __tablename__ = "nodes"
    x_coord: Mapped[int] = mapped_column(nullable=True)
    y_coord: Mapped[int] = mapped_column(nullable=False)
    z_coord: Mapped[int] = mapped_column(nullable=False)
    connections: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    floor: Mapped[int] = mapped_column(nullable=False)
    pid_name: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    landmarks: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
