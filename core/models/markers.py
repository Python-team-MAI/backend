from core.models import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey


class MarkersOrm(Base):
    __tablename__ = "markers"
    value: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)