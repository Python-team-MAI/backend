from app.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api_v1.deadlines.models import DeadlinesOrm

class GroupsOrm(Base):
    __tablename__ = "groups"
    name: Mapped[str] = mapped_column(String(50))

    deadlines: Mapped[list["DeadlinesOrm"]] = relationship(back_populates="group")