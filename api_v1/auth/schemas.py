from pydantic import BaseModel, EmailStr


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class YandexOauthUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr