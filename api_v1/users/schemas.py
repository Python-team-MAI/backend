from pydantic import BaseModel, EmailStr, ConfigDict
import enum

class Role(str, enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"
    HEAD = "head"

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
    role: Role | None = Role.STUDENT
    auth_type: str | None = None
    # json_settings: str


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserCreate(UserBase):
    pass


class UserUpdate(UserCreate):
    pass


class UserUpdatePartialMe(UserCreate):
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None
    email: EmailStr | None = None
    course: int | None = None
    group_id: int | None = None
    institute: int | None = None