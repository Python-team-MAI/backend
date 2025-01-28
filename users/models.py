from core.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from webchat import MessagesOrm
import enum
from sqlalchemy import JSON, String, ForeignKey


class Role(enum.Enum):
    student = "student"
    teacher = "teacher"
    headman = "headman"


class UsersOrm(Base):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(20))
    last_name: Mapped[str] = mapped_column(String(20))
    bio: Mapped[str] = mapped_column(String(256))
    email: Mapped[str]  #TODO email check
    password: Mapped[str]
    course: Mapped[str]
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    institute: Mapped[int]
    role: Mapped[Role]
    json_settings: Mapped[JSON]

    messages: Mapped[list["MessagesOrm"]] = relationship(
        back_populates="users"
        )


class Group(Base):
    __tablename__ = "groups"
    name: Mapped[str] = mapped_column(String(50))




