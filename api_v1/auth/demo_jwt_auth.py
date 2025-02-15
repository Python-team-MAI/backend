from api_v1.users.schemas import User
from api_v1.auth.helpers import create_access_token, create_refresh_token
from api_v1.auth.validation import (
    http_bearer,
    validate_auth_user,
    get_current_auth_user,
    get_current_auth_user_for_refresh,
)
from core.config import settings
from core.models import db_helper
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import TokenInfo, YandexOauthUser
from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

import logging
import api_v1.auth.utils as auth_utils
from .validation import oauth
from fastapi.responses import RedirectResponse
from authlib.integrations.base_client import OAuthError
from authlib.oauth2.rfc6749 import OAuth2Token


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
FRONTEND_URL = "http://localhost:5173/"


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

    user_info = user_response.get("user_info")

    print(user_info)


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

        email_resp = await oauth.github.get('https://api.github.com/user/emails', token=token)
        emails = email_resp.json()
        print(emails[])

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
async def auth_yandex(request: Request):
    try:
        token = await oauth.yandex.authorize_access_token(request)

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не получен.",
            )
        
        # Получение информации о пользователе
        resp = await oauth.yandex.get('https://login.yandex.ru/info', token=token)
        user = resp.json()
        return YandexOauthUser(first_name=user["first_name"], 
                               last_name=user["last_name"],
                               email=user["default_email"])
    except OAuthError as e:
        print(f"OAuthError: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


@router.post("/refresh/", response_model=TokenInfo, response_model_exclude_none=True)
async def auth_refresh_jwt(user: User = Depends(get_current_auth_user_for_refresh)):
    access_token = await create_access_token(user)

    return TokenInfo(access_token=access_token)


@router.post("/login/", response_model=TokenInfo)
async def auth_user_issue_jwt(user: User = Depends(validate_auth_user)):
    access_token = await create_access_token(user=user)
    refresh_token = await create_refresh_token(user=user)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.get("/users/me/")
async def auth_user_check_self_info(
    user: User = Depends(get_current_auth_user),
):
    return {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
    }
