from core.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from sqlalchemy import String, ForeignKey, Boolean

from typing import TYPE_CHECKING



class OfficeOrm(Base):

    __tablename__ = "offices"

    name: Mapped[str]
    description: Mapped[str]
    


