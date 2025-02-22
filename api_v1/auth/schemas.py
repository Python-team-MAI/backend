from pydantic import BaseModel, EmailStr
from enum import Enum


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class OauthUser(BaseModel):
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

