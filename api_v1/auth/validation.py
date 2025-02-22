from api_v1.users.schemas import UserRead
from api_v1.users.crud import get_user_by_email, get_user_by_id
from api_v1.auth.helpers import (
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TOKEN_TYPE,
    REFRESH_TOKEN_TOKEN_TYPE,
)
from .schemas import UserLogin
from api_v1.users.schemas import Role
from core.config import settings
from core.models import db_helper
from starlette.config import Config
from fastapi import HTTPException, status, Depends, Form
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
import api_v1.auth.utils as auth_utils
from jwt import InvalidTokenError

http_bearer = HTTPBearer(auto_error=False)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/")


GOOGLE_CLIENT_ID = settings.oauth2.AUTH_GOOGLE_ID
GOOGLE_CLIENT_SECRET = settings.oauth2.AUTH_GOOGLE_SECRET
GITHUB_CLIENT_ID = settings.oauth2.AUTH_GITHUB_ID
GITHUB_CLIENT_SECRET = settings.oauth2.AUTH_GITHUB_SECRET
YANDEX_CLIENT_ID=settings.oauth2.AUTH_YANDEX_ID
YANDEX_CLIENT_SECRET=settings.oauth2.AUTH_YANDEX_SECRET


if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise Exception("Missing env variables")

config_data = {
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
    "GITHUB_CLIENT_ID": GITHUB_CLIENT_ID,
    "GITHUB_CLIENT_SECRET": GITHUB_CLIENT_SECRET,
    "YANDEX_CLIENT_ID": YANDEX_CLIENT_ID,
    "YANDEX_CLIENT_SECRET": YANDEX_CLIENT_SECRET
}

starlette_config = Config(environ=config_data)

oauth = OAuth(starlette_config)

# Регистрация Google
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid email profile"
    },
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
    user: UserLogin,
    session=Depends(db_helper.session_dependency),
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid password or username"
    )
    user = await get_user_by_email(session=session, email=user.email)
    
    if not user:
        raise unauthed_exc
    if auth_utils.validate_password(
        password=user.password, hashed_password=user.password
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

def role_required(required_role: Role):
    async def check_role(user: str = Depends(get_current_auth_user)):
         # Твоя функция для получения пользователя из токена
        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource",
            )
        return user
    return check_role


async def get_user_by_token_sub(payload: dict, session) -> UserRead:
    user_id = int(payload.get("sub"))
    user = await get_user_by_id(session=session, user_id=user_id)
    if user is not None:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found"
    )

async def get_email_from_token(token: str):
    payload = auth_utils.decode_jwt(token=token)
    return {"email": payload["sub"], "auth_type": payload["auth_typ"]}


async def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = auth_utils.decode_jwt(token=token)
    except InvalidTokenError as e:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token error. Not enough segments",
        )
    return payload


def get_auth_user_from_token_of_type(token_type: str):
    async def get_current_auth_user_from_token(
        payload: dict = Depends(get_current_token_payload),
        session=Depends(db_helper.session_dependency),
    ):
        await validate_token_type(payload=payload, token_type=token_type)
        return await get_user_by_token_sub(payload=payload, session=session)

    return get_current_auth_user_from_token


get_current_auth_user = get_auth_user_from_token_of_type(ACCESS_TOKEN_TOKEN_TYPE)
get_current_auth_user_for_refresh = get_auth_user_from_token_of_type(
    REFRESH_TOKEN_TOKEN_TYPE
)
