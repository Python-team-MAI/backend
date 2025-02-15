from core.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .messages import MessagesOrm


class Role(enum.Enum):
    student = "student"
    teacher = "teacher"
    headman = "headman"


class UsersOrm(Base):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(20))
    last_name: Mapped[str] = mapped_column(String(20))
    bio: Mapped[str] = mapped_column(String(256))
    email: Mapped[str]  # TODO email check
    password: Mapped[bytes]
    auth_type: Mapped[str]
    course: Mapped[int]
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    institute: Mapped[int]
    role: Mapped[str]
    # json_settings: Mapped[JSON]

    messages: Mapped[list["MessagesOrm"]] = relationship(back_populates="user")
