from app.core.base.base_repository import BaseRepository
from app.api_v1.offices.models import OfficesOrm
from app.api_v1.offices.schemas import OfficeFilter
from app.api_v1.chats.models import ChatsOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.api_v1.utils.setup_logging import setup_logging

logger = setup_logging(__name__)


class OfficesRepo(BaseRepository):
    model = OfficesOrm

    async def find_all_with_chat(
        self,
        session: AsyncSession,
        filters: OfficeFilter | None = None,
    ):
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.debug(
            f"Поиск всех записей {self.model.__name__} по фильтрам: {filter_dict}"
        )
        query = (
            select(self.model)
            .filter_by(**filter_dict)
            .options(selectinload(OfficesOrm.chat))
        )
        result = await session.execute(query)
        records = result.scalars().all()
        logger.debug(f"Найдено {len(records)} записей.")
        return records


offices_repo: OfficesOrm = OfficesRepo()
