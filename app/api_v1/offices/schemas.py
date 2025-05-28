from pydantic import BaseModel, EmailStr, ConfigDict
import enum
from datetime import datetime


class Office(BaseModel):
    desc: str | None
    name: str
    color: str
    length: int
    width: int
    floor: int
    height: int
    type: str
    coords: list[float]



class OfficeRead(Office):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime
    id: int

class OfficeCreate(Office):
    pass


class OfficeUpdate(OfficeCreate):
    pass


class OfficeFilter(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    desc: str | None = None
    name: str | None = None
    color: str | None = None
    length: int | None = None
    width: int | None = None
    height: int | None = None
    floor: int | None = None
    type: str | None = None
    coords: list[int] | None = None
