import dns.exception
from app.api_v1.users.schemas import UserRead, UserFilter, UserCreate
from app.api_v1.users.service import users_service
from app.api_v1.users.dependencies import user_by_email, user_by_id
from app.api_v1.users.models import UsersOrm
from app.api_v1.auth.helpers import (
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TOKEN_TYPE,
    REFRESH_TOKEN_TOKEN_TYPE,
)
from .schemas import UserLogin
from app.api_v1.users.schemas import Role
from app.api_v1.utils.exceptions import (
    PasswordHasNoDigitsError,
    PasswordHasNoLowerCaseError,
    PasswordHasNoSpecialError,
    PasswordHasNoUpperCaseError,
)
from app.core.config import settings
from app.core.session_manager import SessionDep
from starlette.config import Config
from fastapi import HTTPException, status, Depends, Form, Request
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
import app.api_v1.auth.utils as auth_utils
from pydantic import EmailStr
from jwt import InvalidTokenError
import dns.resolver
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, datetime, timezone
import logging
import re

logger = logging.getLogger(__name__)

http_bearer = HTTPBearer(auto_error=False)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


GOOGLE_CLIENT_ID = settings.oauth2.AUTH_GOOGLE_ID
GOOGLE_CLIENT_SECRET = settings.oauth2.AUTH_GOOGLE_SECRET
GITHUB_CLIENT_ID = settings.oauth2.AUTH_GITHUB_ID
GITHUB_CLIENT_SECRET = settings.oauth2.AUTH_GITHUB_SECRET
YANDEX_CLIENT_ID = settings.oauth2.AUTH_YANDEX_ID
YANDEX_CLIENT_SECRET = settings.oauth2.AUTH_YANDEX_SECRET
BACKEND_HOST = settings.hosts.BACKEND_HOST
FRONTEND_HOST = settings.hosts.FRONTEND_HOST
GOOGLE_REDIRECT_URI = f"{BACKEND_HOST}v1/auth/callback/google"
GITHUB_REDIRECT_URI = f"{BACKEND_HOST}v1/auth/callback/github"
YANDEX_REDIRECT_URI = f"{BACKEND_HOST}v1/auth/callback/yandex"

if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise Exception("Missing env variables")

config_data = {
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
    "GITHUB_CLIENT_ID": GITHUB_CLIENT_ID,
    "GITHUB_CLIENT_SECRET": GITHUB_CLIENT_SECRET,
    "YANDEX_CLIENT_ID": YANDEX_CLIENT_ID,
    "YANDEX_CLIENT_SECRET": YANDEX_CLIENT_SECRET,
}

starlette_config = Config(environ=config_data)

oauth = OAuth(starlette_config)

# Регистрация Google
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={"scope": "openid email profile"},
)
# Регистрация GitHub
oauth.register(
    name="github",
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    client_kwargs={"scope": "user:email"},
)

# Регистрация Яндекс
oauth.register(
    name="yandex",
    client_id=YANDEX_CLIENT_ID,
    client_secret=YANDEX_CLIENT_SECRET,
    authorize_url="https://oauth.yandex.ru/authorize",
    access_token_url="https://oauth.yandex.ru/token",
    client_kwargs={"scope": "login:email login:info"},
)


async def validate_auth_user(
    user_in: UserLogin,
    session=SessionDep,
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid password or username"
    )
    unverify_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="your email dont verify"
    )
    user = await users_service.find_one_or_none(
        session=session, filters=UserFilter(email=user_in.email)
    )

    if not user:
        raise unauthed_exc
    # if not user.is_verified:
    #     raise unverify_exc
    if auth_utils.validate_password(
        password=user_in.password, hashed_password=user.password
    ):
        return user

    raise unauthed_exc


async def validate_token_type(payload: dict, token_type: str) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"invalid token type {current_token_type!r} expected {token_type!r}",
    )


async def validate_token(token: str | bytes, token_type: str):
    try:

        payload = auth_utils.decode_jwt(token=token)
        await validate_token_type(payload=payload, token_type=token_type)
        if payload["exp"] < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"token has expired",
            )

        return {"success": True, "error": None}

    except Exception as e:
        return {"success": False, "error": e}


def validate_password(password: str) -> int:
    has_lower = re.search(r"[a-z]", password)
    has_upper = re.search(r"[A-Z]", password)
    has_digit = re.search(r"\d", password)
    has_special = re.search(r"[^A-Za-z0-9]", password)
    if len(password) > 10 and has_lower and has_upper and has_digit and has_special:
        return 3
    elif len(password) > 8 and (has_lower or has_upper) and has_digit:
        return 2
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bad Password. Security level is 1",
        )


def validate_email(email: EmailStr) -> bool:
    domain = str(email).split("@")[-1]
    try:
        records = dns.resolver.resolve(domain, "MX")
        logger.debug(f"Records: {records}")
        return bool(records)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
        return False


async def validate_user_email_and_password(user: UserLogin, session: AsyncSession):
    email = user.email
    password = user.password
    if not validate_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not valid. Domain does not exist",
        )
    logger.debug("Check email - Success")
    if await users_service.find_one_or_none(
        session=session, filters=UserFilter(email=email)
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exist",
        )
    logger.debug("Check user exist - Success")
    if user.password:
        security_level = validate_password(password=password)
        logger.debug(f"Password security level: {security_level}")

    logger.debug("Check password - Success")
    logger.info("Success user credentionals validation ")
    return True


def require_condition(required_role: str | None = None, allow_superuser: bool = True):
    async def checker(user: UserRead = Depends(get_current_auth_user)):
        if allow_superuser and user.is_superuser:
            return user

        if required_role and user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}",
            )

        return user

    return checker


# Для проверки суперпользователя
def require_superuser():
    async def checker(user: UserRead = Depends(get_current_auth_user)):
        if not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Superuser required",
            )
        return user

    return checker


# Для проверки роли с учетом суперпользователя
def require_role(required_role: str):
    return require_condition(required_role=required_role, allow_superuser=True)


async def get_user_by_token_sub(payload: dict, session) -> UserRead:
    user_id = int(payload.get("sub"))
    logger.info(f"Current user: {user_id}")
    user = await users_service.find_one_or_none(
        session=session, filters=UserFilter(id=user_id)
    )
    if user is not None:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found"
    )


async def get_email_from_token(token: str):
    payload = auth_utils.decode_jwt(token=token)
    return {"email": payload["sub"], "auth_type": payload["auth_typ"]}


async def get_token_from_cookie_or_header(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        authorization_header = request.headers.get("Authorization")
        logger.info(f"Authorization header: {authorization_header}")
        if authorization_header:
            token = authorization_header.replace("Bearer ", "")
        else:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

    return token


async def get_current_token_payload(
    token: str = Depends(get_token_from_cookie_or_header),
) -> dict:
    try:

        payload = auth_utils.decode_jwt(token=token)
    except InvalidTokenError as e:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token error. Not enough segments",
        )
    return payload


async def get_current_user_role(
    payload: dict = Depends(get_current_token_payload),
) -> str:
    role = payload.get("role")
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role not found in token",
        )
    return role


def get_auth_user_from_token_of_type(token_type: str):
    async def get_current_auth_user_from_token(
        payload: dict = Depends(get_current_token_payload),
        session=SessionDep,
    ):
        await validate_token_type(payload=payload, token_type=token_type)
        return await get_user_by_token_sub(payload=payload, session=session)

    return get_current_auth_user_from_token


get_current_auth_user = get_auth_user_from_token_of_type(ACCESS_TOKEN_TOKEN_TYPE)
get_current_auth_user_for_refresh = get_auth_user_from_token_of_type(
    REFRESH_TOKEN_TOKEN_TYPE
)
