from pydantic import BaseModel, ConfigDict
from datetime import datetime


class Deadline(BaseModel):
    name: str
    date_from: datetime
    date_to: datetime
    teacher: str | None
    author_id: int
    group_id: int
    lesson: str | None
    description: str | None


class DeadlineRead(Deadline):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class DeadlineCreate(Deadline):
    pass


class DeadlineUpdate(DeadlineCreate):
    pass


class DeadlineFilter(DeadlineCreate):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    name: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    teacher: str | None = None
    author_id: int | None = None
    group_id: int | None = None
    lesson: str | None = None
    description: str | None = None
