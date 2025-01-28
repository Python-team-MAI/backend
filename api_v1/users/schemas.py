from pydantic import BaseModel, EmailStr, ConfigDict
import enum

class UserBase(BaseModel):
    first_name: str 
    last_name: str
    bio: str
    email: EmailStr
    password: str
    course: int
    group_id: int
    institute: int
    # role: enum.Enum
    # json_settings: str

class User(UserBase):
    model_config  = ConfigDict(from_attributes=True)

    id: int

class UserCreate(UserBase):
    pass