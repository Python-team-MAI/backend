from pydantic import BaseModel, EmailStr, ConfigDict
import enum

class UserBase(BaseModel):
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
    role: str | None = None
    auth_type: str | None = None
    # json_settings: str


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserCreate(UserBase):
    pass


class UserUpdate(UserCreate):
    pass


class UserUpdatePartial(UserCreate):
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False
    bio: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    course: int | None = None
    group_id: int | None = None
    institute: int | None = None
    auth_type: str | None = None
    role: str | None = None