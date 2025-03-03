from core.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

class RefreshToken(Base):
    jti: Mapped[str] = mapped_column(primary_key=True)
    sub: Mapped[str] = mapped_column(on_delete='CASCADE')
    revoked: Mapped[bool]