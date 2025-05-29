from app.core.base.base_repository import BaseRepository
from app.api_v1.assistant.models import KnowledgeSnapshotsOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


class KnowledgeSnapshotsRepo(BaseRepository):
    model = KnowledgeSnapshotsOrm


snapshots_repo: KnowledgeSnapshotsRepo = KnowledgeSnapshotsRepo()