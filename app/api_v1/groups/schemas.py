from pydantic import BaseModel, ConfigDict
from datetime import datetime


class Group(BaseModel):
    name: str


class GroupRead(Group):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class GroupCreate(Group):
    pass


class GroupUpdate(GroupCreate):
    pass


class GroupFilter(GroupCreate):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    name: str | None = None
