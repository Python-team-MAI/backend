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


class Node(BaseModel):
    x_coord: int
    y_coord: int
    z_coord: int
    connections: list[str]
    floor: int
    pid_name: str
    type: str
    landmarks: list[str]
    name: str


class OfficeRead(Office):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime
    id: int


class NodeRead(Node):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime
    id: int

class OfficeCreate(Office):
    pass

class NodeCreate(Node):
    pass


class OfficeUpdate(OfficeCreate):
    pass


class OfficeFilter(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    desc: str | None
    name: str | None = None
    color: str | None = None
    length: int | None = None
    width: int | None = None
    height: int | None = None
    floor: int | None = None
    type: str | None = None
    coords: list[int] | None = None

class NodeFilter(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    x_coord: int | None = None
    y_coord: int | None = None
    z_coord: int | None = None
    connections: list[str] | None = None
    floor: int | None = None
    pid_name: str | None = None
    type: str | None = None
    landmarks: list[str] | None = None
    name: str | None = None