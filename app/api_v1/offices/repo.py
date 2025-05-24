from app.core.base.base_repository import BaseRepository
from app.api_v1.offices.models import OfficesOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


class OfficesRepo(BaseRepository):
    model = OfficesOrm


offices_repo: OfficesOrm = OfficesRepo()
