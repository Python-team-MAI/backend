from pydantic import BaseModel, EmailStr, ConfigDict
import enum


class UserBase(BaseModel):
    first_name: str
    last_name: str
    bio: str
    email: EmailStr | None = None
    password: bytes | None
    course: int
    group_id: int
    institute: int
    role: str
    auth_type: str
    # json_settings: str


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserCreate(UserBase):
    pass


class UserUpdate(UserCreate):
    pass


class UserUpdatePartial(UserCreate):
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    course: int | None = None
    group_id: int | None = None
    institute: int | None = None
    auth_type: str | None = None
