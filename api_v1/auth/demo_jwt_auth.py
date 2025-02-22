from api_v1.users.schemas import UserRead, UserCreate
from api_v1.users.crud import get_user_by_email, create_user
from api_v1.auth.helpers import create_access_token, create_refresh_token, create_register_token
from api_v1.auth.validation import (
    http_bearer,
    validate_auth_user,
    get_current_auth_user,
    get_current_auth_user_for_refresh,
)
from core.config import settings
from core.models import db_helper
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import TokenInfo, UserLogin
from fastapi import APIRouter, Depends, Request, status, HTTPException, Body

from .validation import oauth
from fastapi.responses import RedirectResponse
from authlib.integrations.base_client import OAuthError
from authlib.oauth2.rfc6749 import OAuth2Token
import json

router = APIRouter(prefix="/auth", tags=["Auth"], dependencies=[Depends(http_bearer)])


GOOGLE_CLIENT_ID = settings.oauth2.AUTH_GOOGLE_ID
GOOGLE_CLIENT_SECRET = settings.oauth2.AUTH_GOOGLE_SECRET
GITHUB_CLIENT_ID = settings.oauth2.AUTH_GITHUB_ID
GITHUB_CLIENT_SECRET = settings.oauth2.AUTH_GITHUB_SECRET
YANDEX_CLIENT_ID = settings.oauth2.AUTH_YANDEX_ID
YANDEX_CLIENT_SECRET = settings.oauth2.AUTH_YANDEX_SECRET
BACKEND_HOST = settings.oauth2.BACKEND_HOST
FRONTEND_HOST = settings.oauth2.FRONTEND_HOST
GOOGLE_REDIRECT_URI = f"{BACKEND_HOST}/api/v1/auth/callback/google/"
GITHUB_REDIRECT_URI = f"{BACKEND_HOST}/api/v1/auth/callback/github/"
YANDEX_REDIRECT_URI = f"{BACKEND_HOST}/api/v1/auth/callback/yandex/"

@router.get("/google/")
async def login_google(request: Request):
    return await oauth.google.authorize_redirect(request, GOOGLE_REDIRECT_URI)


@router.get("/callback/google/")
async def auth_google(
    request: Request, session: AsyncSession = Depends(db_helper.session_dependency)
):
    try:
        user_response: OAuth2Token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user_info = user_response.get("userinfo")
    email = user_info["email"].lower()
    user = await get_user_by_email(session=session, email=email)

    if user:
        token = await create_access_token(user=user)
        return RedirectResponse(f"{settings.oauth2.FRONTEND_HOST}/api/v1/auth/callback?token={token}")
    else:
        token = await create_register_token(email=email, auth_type="google")
        
        return RedirectResponse(f"{settings.oauth2.FRONTEND_HOST}/api/v1/auth/callback?token={token}")


@router.get("/github/")
async def login_github(request: Request):
    return await oauth.github.authorize_redirect(request, GITHUB_REDIRECT_URI)


@router.get("/callback/github/")
async def auth_github(
    request: Request, session: AsyncSession = Depends(db_helper.session_dependency)
):
    try:
        token = await oauth.github.authorize_access_token(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не получен.",
            )
        users_resp = await oauth.github.get('https://api.github.com/user', token=token)
        user = users_resp.json()
        email_resp = await oauth.github.get('https://api.github.com/user/emails', token=token)
        email = email_resp.json()[0]["email"].lower()
        user = await get_user_by_email(session=session, email=email)
        if user:
            token = await create_access_token(user=user)
            return RedirectResponse(f"{settings.oauth2.FRONTEND_HOST}/api/v1/auth/callback?token={token}")
        else:
            token = await create_register_token(email=email, auth_type="github")
            return RedirectResponse(f"{settings.oauth2.FRONTEND_HOST}/api/v1/auth/callback?token={token}")

    except OAuthError as e:
        print(f"OAuthError: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


@router.get("/yandex/")
async def login_github(request: Request):
    return await oauth.yandex.authorize_redirect(request, YANDEX_REDIRECT_URI)


@router.get("/callback/yandex/")
async def auth_yandex(request: Request, session: AsyncSession = Depends(db_helper.session_dependency)):
    try:
        token = await oauth.yandex.authorize_access_token(request)

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не получен.",
            )
        
        # Получение информации о пользователе
        resp = await oauth.yandex.get('https://login.yandex.ru/info', token=token)
        user_info = resp.json()
        email = user_info["default_email"].lower()

        user = await get_user_by_email(session=session, email=email)
        if user:
            token = await create_access_token(user=user)
            return RedirectResponse(f"{settings.oauth2.FRONTEND_HOST}/api/v1/auth/callback?token={token}")
        else:
            token = await create_register_token(email=email, auth_type="yandex")
            return RedirectResponse(f"{settings.oauth2.FRONTEND_HOST}/api/v1/auth/callback?token={token}")
        
    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


@router.post("/refresh/", response_model=TokenInfo, response_model_exclude_none=True)
async def auth_refresh_jwt(user: UserRead = Depends(get_current_auth_user_for_refresh)):
    access_token = await create_access_token(user)

    return TokenInfo(access_token=access_token)


@router.post("/login/", response_model=TokenInfo)
async def auth_user_issue_jwt(user: UserRead = Depends(validate_auth_user)):

    access_token = await create_access_token(user=user)
    refresh_token = await create_refresh_token(user=user)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.get("/users/me/")
async def auth_user_check_self_info(
    user: UserRead = Depends(get_current_auth_user),
):
    return user

@router.post("/register/")
async def register_user(user: UserLogin, session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    print(user, user.email, user.password)
    # if await get_user_by_email(session=session, email=new_user.email):
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exist")
    # #TODO some validation
    # user = UserCreate(email=new_user.email, password=new_user.password, auth_type="default")
    # await create_user(session=session, user_in=user)
    # access_token = await create_access_token(user=user)
    # refresh_token = await create_refresh_token(user=user)
    # return TokenInfo(access_token=access_token, refresh_token=refresh_token)

# @router.get("/")
# async def test(token):
#     return token