from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime


from typing import Annotated


def parse_datetime(value):
    if isinstance(value, str):
        dt = datetime.fromisoformat(value)
    elif isinstance(value, datetime):
        dt = value
    else:
        raise ValueError("Invalid datetime format")
    
    # Явно обрезаем микросекунды и часовой пояс
    return dt.replace(microsecond=0, tzinfo=None)

class Deadline(BaseModel):
    name: str
    date_from: datetime | None 
    date_to: datetime
    teacher: str | None
    author_id: int
    lesson: str | None
    description: str | None

    @field_validator('date_from', 'date_to', mode='before')
    def parse_datetime(cls, value):
        if isinstance(value, str):
            dt = datetime.fromisoformat(value)
        elif isinstance(value, datetime):
            dt = value
        else:
            raise ValueError("Invalid datetime format")
        
        # Явно обрезаем микросекунды и часовой пояс
        return dt.replace(microsecond=0, tzinfo=None)


class DeadlineRead(Deadline):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime




class PersonalDeadlineCreate(Deadline):
    pass

class GroupDeadlineCreate(Deadline):
    group_id: int


class DeadlineUpdate(BaseModel):
    name: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    teacher: str | None = None
    lesson: str | None = None
    description: str | None = None


class DeadlineFilter(BaseModel):
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
