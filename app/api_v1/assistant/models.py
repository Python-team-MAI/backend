from app.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey
from typing import TYPE_CHECKING, Optional
from sqlalchemy.dialects.postgresql import JSONB


class KnowledgeSnapshotsOrm(Base):
    __tablename__ = "knowledge_snapshots"

    is_active: Mapped[bool] = mapped_column(default=False)
    document_paths: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    index_id: Mapped[str] = mapped_column(nullable=True)       # ID индекса в Yandex GPT
    status: Mapped[str] = mapped_column(String, default='pending')     # pending, processing, ready, failed
