import app.api_v1.auth.utils as auth_utils
from app.api_v1.users.schemas import UserRead
from app.core.config import settings
from datetime import timedelta
from .schemas import TokenInfo
import logging
from app.api_v1.utils.setup_logging import setup_logging
from app.core.redis_helper import redis_helper
from fastapi import Depends
from redis.asyncio import Redis
logger = setup_logging(__name__)
TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TOKEN_TYPE = "access"
REFRESH_TOKEN_TOKEN_TYPE = "refresh"
from uuid import UUID, uuid4

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



async def set_issue_auth_code(user_id: int, redis: Redis):
    code = str(uuid4())
    await redis.set(f"auth_code:{code}", str(user_id), ex=120)
    
    logger.debug(f"Set code: {code}. User_id: {user_id}")
    return code

async def create_access_token(user: UserRead) -> str:
    jwt_payload = {
        "sub": str(user.id),  # subject
        "email": user.email,
        "role": user.role.value if user.role else None,
    }
    logger.debug("Создаем access токен")
    return await create_jwt(
        token_type=ACCESS_TOKEN_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )


async def create_refresh_token(user: UserRead) -> str:
    jwt_payload = {"sub": str(user.id)}
    logger.debug("Создаем refresh токен")
    return await create_jwt(
        token_type=REFRESH_TOKEN_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )


async def setup_access_token(user):
    access_token = await create_access_token(user)
    return access_token


async def setup_refresh_token(user):
    refresh_token = await create_refresh_token(user)
    return refresh_token
