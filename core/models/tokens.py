from core.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey, Boolean

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chats import ChatsOrm


class RefreshToken(Base):
    jti: Mapped[str] = mapped_column(primary_key=True)
    sub: Mapped[str] = mapped_column(on_delete='CASCADE')
    revoked: Mapped[bool]