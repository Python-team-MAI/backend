from pydantic import BaseModel, EmailStr
from enum import Enum


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class OauthUser(BaseModel):
    email: EmailStr

class NewUserDefault(BaseModel):
    email: EmailStr
    password: str
    auth_type: str = "default"


class Role(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
    HEAD = "head"