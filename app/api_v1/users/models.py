from app.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey, Boolean

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api_v1.groups.models import GroupsOrm
    from app.api_v1.deadlines.models import DeadlinesOrm



class Role(enum.Enum):
    student = "student"
    teacher = "teacher"
    headman = "headman"


class UsersOrm(Base):
    __tablename__ = "users"
    first_name: Mapped[str] = mapped_column(String(20), nullable=True)
    last_name: Mapped[str] = mapped_column(String(20), nullable=True)
    bio: Mapped[str] = mapped_column(String(256), nullable=True)
    email: Mapped[str]  = mapped_column(nullable=False)
    password: Mapped[bytes] = mapped_column(nullable=True)
    auth_type: Mapped[str] = mapped_column(nullable=True)
    course: Mapped[int] = mapped_column(nullable=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)
    institute: Mapped[int] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    deadlines: Mapped[list["DeadlinesOrm"]] = relationship("DeadlinesOrm", back_populates="author")
    group: Mapped["GroupsOrm"] = relationship(back_populates="users")
