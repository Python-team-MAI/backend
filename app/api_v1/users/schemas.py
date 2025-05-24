from pydantic import BaseModel, EmailStr, ConfigDict
import enum
from datetime import datetime


class Role(str, enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"
    HEAD = "head"


class User(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    bio: str | None = None
    email: EmailStr
    password: bytes | None
    course: int | None = None
    group_id: int | None = None
    institute: int | None = None
    role: Role | None = Role.STUDENT
    auth_type: str
    # json_settings: str


class UserRead(User):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: datetime
    id: int


class UserCreate(User):
    pass


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None
    password: bytes | None = None
    course: int | None = None
    group_id: int | None = None
    institute: int | None = None
    is_superuser: bool | None = None
    role: Role | None = None


class UserFilter(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None
    bio: str | None = None
    email: EmailStr | None = None
    password: bytes | None = None
    course: int | None = None
    group_id: int | None = None
    institute: int | None = None
    role: Role | None = None
    auth_type: str | None = None
