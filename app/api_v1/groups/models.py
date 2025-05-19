from app.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class GroupsOrm(Base):
    __tablename__ = "groups"
    name: Mapped[str] = mapped_column(String(50))