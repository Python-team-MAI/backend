from pydantic import BaseModel, EmailStr, ConfigDict
import enum
from datetime import datetime


class Office(BaseModel):
    desc: str | None
    name: str
    color: str
    length: float
    width: float
    floor: int
    height: float
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
    length: float | None = None
    width: float | None = None
    height: float | None = None
    floor: int | None = None
    type: str | None = None
    coords: list[float] | None = None
