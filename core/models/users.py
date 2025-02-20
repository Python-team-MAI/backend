from core.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey, Boolean

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .messages import MessagesOrm


class Role(enum.Enum):
    student = "student"
    teacher = "teacher"
    headman = "headman"


class UsersOrm(Base):
    __tablename__ = "users"
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False)
    bio: Mapped[str] = mapped_column(String(256))
    email: Mapped[str]  = mapped_column(nullable=False)
    password: Mapped[bytes] = mapped_column(nullable=True)
    auth_type: Mapped[str] = mapped_column(nullable=False)
    course: Mapped[int] = mapped_column(nullable=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)
    institute: Mapped[int] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    # json_settings: Mapped[JSON]

    messages: Mapped[list["MessagesOrm"]] = relationship(back_populates="user")

