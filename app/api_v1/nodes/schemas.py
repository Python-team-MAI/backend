from pydantic import BaseModel, ConfigDict
from datetime import datetime

class Node(BaseModel):
    x: float
    y: float
    z: float
    connections: list[str]
    floor: int
    pid_name: str
    type: str
    landmarks: list[str]
    name: str


class NodeRead(Node):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime
    id: int

class NodeCreate(Node):
    pass


class NodeFilter(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    x_coord: float | None = None
    y_coord: float | None = None
    z_coord: float | None = None
    connections: list[str] | None = None
    floor: int | None = None
    pid_name: str | None = None
    type: str | None = None
    landmarks: list[str] | None = None
    name: str | None = None