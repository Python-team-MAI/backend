from pydantic import BaseModel, EmailStr, ConfigDict
import enum
from datetime import datetime


class Office(BaseModel):
    name: str
    description: str | None 


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
    name: str | None = None
    description: str | None = None
