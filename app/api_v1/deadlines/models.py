from app.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey, Boolean, DateTime
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api_v1.groups.models import GroupsOrm
    from app.api_v1.users.models import UsersOrm


class DeadlinesOrm(Base):
    __tablename__ = "deadlines"
    name: Mapped[str] = mapped_column(nullable=False)
    date_from: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=True)
    date_to: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    teacher: Mapped[str] = mapped_column(String(50), nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=True
    )
    lesson: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    group: Mapped["GroupsOrm"] = relationship("GroupsOrm", back_populates="deadlines")
    author: Mapped["UsersOrm"] = relationship("UsersOrm", back_populates="deadlines")
