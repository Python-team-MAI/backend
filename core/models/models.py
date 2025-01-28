from core.models import Base, created_at, updated_at
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import JSON, String, ForeignKey


class Role(enum.Enum):
    student = "student"
    teacher = "teacher"
    headman = "headman"

class ChatType(enum.Enum):
    default = "default"


class UsersOrm(Base):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(20))
    last_name: Mapped[str] = mapped_column(String(20))
    bio: Mapped[str] = mapped_column(String(256))
    email: Mapped[str]  #TODO email check
    password: Mapped[str]
    course: Mapped[int]
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    institute: Mapped[int]
    # role: Mapped[Role]
    # json_settings: Mapped[JSON]

    messages: Mapped[list["MessagesOrm"]] = relationship(
        back_populates="user"
        )


class GroupsOrm(Base):
    __tablename__ = "groups"
    name: Mapped[str] = mapped_column(String(50))


class MessagesOrm(Base):
    __tablename__ = "messages"

    text: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))
    # media_id: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    is_deleted: Mapped[bool]
    is_anonyumus: Mapped[bool]

    user: Mapped["UsersOrm"] = relationship(
        back_populates="messages"
    )


class ChatsOrm(Base):
    __tablename__ = "chats"

    name: Mapped[str] = mapped_column(String(50))
    type: Mapped[ChatType]
    institute: Mapped[int]
    # office_id: Mapped[int]
