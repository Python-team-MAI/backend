import api_v1.auth.utils as auth_utils
from api_v1.users.schemas import UserRead
from core.config import settings
from datetime import timedelta
from .schemas import TokenInfo


TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TOKEN_TYPE = "access"
REFRESH_TOKEN_TOKEN_TYPE = "refresh"


async def create_jwt(
    token_type: str,
    token_data: dict,
    expire_timedelta: timedelta | None = None,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
) -> dict:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return auth_utils.encode_jwt(
        payload=jwt_payload,
        expire_minute=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


async def create_access_token(user: UserRead) -> str:
    jwt_payload = {
        "sub": str(user.id),  # subject
        "email": user.email,
        "role": user.role
    }
    return await create_jwt(
        token_type=ACCESS_TOKEN_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )


async def create_refresh_token(user: UserRead) -> str:
    jwt_payload = {"sub": str(user.id)}
    return await create_jwt(
        token_type=REFRESH_TOKEN_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )



async def setup_access_token(user, response):
    access_token = await create_access_token(user)
    response.set_cookie(
        "access_token",
        access_token,
        expires=settings.auth_jwt.access_token_expire_minutes * 60,
        samesite="strict",
        httponly=True,
    )
    return access_token


async def setup_refresh_token(user, response):
    refresh_token = await create_refresh_token(user)
    response.set_cookie(
        "refresh_token",
        refresh_token,
        expires=settings.auth_jwt.refresh_token_expire_days * 60 * 60 * 24,
        samesite="strict",
        httponly=True,
    )
    return refresh_token
