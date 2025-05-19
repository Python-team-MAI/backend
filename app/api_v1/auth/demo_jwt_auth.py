from app.api_v1.users.schemas import UserRead, UserCreate, UserUpdate, UserFilter
from app.api_v1.users.service import users_service
from app.api_v1.auth.helpers import create_access_token, create_refresh_token, setup_access_token, setup_refresh_token
from app.api_v1.auth.validation import (
    http_bearer,
    validate_auth_user,
    get_current_auth_user,
    get_current_auth_user_for_refresh,
)
from app.core.config import settings
from app.core.session_manager import SessionDep
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import TokenInfo, UserLogin
from fastapi import APIRouter, Depends, Request, status, HTTPException, Body, Response

from .validation import oauth, require_role, validate_token
from fastapi.responses import RedirectResponse
from authlib.integrations.base_client import OAuthError
from authlib.oauth2.rfc6749 import OAuth2Token
import logging

router = APIRouter(prefix="/auth", tags=["Auth"], dependencies=[Depends(http_bearer)])
logger = logging.getLogger(__name__)

GOOGLE_CLIENT_ID = settings.oauth2.AUTH_GOOGLE_ID
GOOGLE_CLIENT_SECRET = settings.oauth2.AUTH_GOOGLE_SECRET
GITHUB_CLIENT_ID = settings.oauth2.AUTH_GITHUB_ID
GITHUB_CLIENT_SECRET = settings.oauth2.AUTH_GITHUB_SECRET
YANDEX_CLIENT_ID = settings.oauth2.AUTH_YANDEX_ID
YANDEX_CLIENT_SECRET = settings.oauth2.AUTH_YANDEX_SECRET
BACKEND_HOST = settings.oauth2.BACKEND_HOST
FRONTEND_HOST = settings.oauth2.FRONTEND_HOST
GOOGLE_REDIRECT_URI = f"{BACKEND_HOST}/v1/auth/callback/google"
GITHUB_REDIRECT_URI = f"{BACKEND_HOST}/v1/auth/callback/github"
YANDEX_REDIRECT_URI = f"{BACKEND_HOST}/v1/auth/callback/yandex"



@router.get("/google")
async def login_google(request: Request):
    return await oauth.google.authorize_redirect(request, GOOGLE_REDIRECT_URI)


@router.get("/callback/google")
async def auth_google(
    response: Response, request: Request, session: AsyncSession = SessionDep
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
    logger.info(f"Get user email from google: {email}")
    user = await users_service.find_one_or_none(session=session, filters=UserFilter(email=email))
    if user:
        await setup_access_token(user=user, response=response)
        return RedirectResponse(f"{settings.oauth2.FRONTEND_HOST}/api/v1/auth/callback")
    else:
        user = UserCreate(email=email, password=None, auth_type="google")
        user = await users_service.add(session=session, values=user)
        await setup_access_token(user=user, response=response)
        return RedirectResponse(f"{settings.oauth2.FRONTEND_HOST}/api/v1/auth/callback")


@router.get("/github")
async def login_github(request: Request):
    return await oauth.github.authorize_redirect(request, GITHUB_REDIRECT_URI)


@router.get("/callback/github")
async def auth_github(
    request: Request, session: AsyncSession = SessionDep
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
        user = await users_service.find_one_or_none(session=session, filters=UserFilter(email=email))
        if user:
            setup_access_token(user=user)
            return RedirectResponse(f"{settings.oauth2.FRONTEND_HOST}/api/v1/auth/callback")
        else:
            user = UserCreate(email=email, password=None, auth_type="github")
            user = await users_service.add(session=session, values=user)
            setup_access_token(user=user)
            return RedirectResponse(f"{settings.oauth2.FRONTEND_HOST}/api/v1/auth/callback")

    except OAuthError as e:
        print(f"OAuthError: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


@router.get("/yandex")
async def login_github(request: Request):
    return await oauth.yandex.authorize_redirect(request, YANDEX_REDIRECT_URI)


@router.get("/callback/yandex")
async def auth_yandex(response: Response, request: Request, session: AsyncSession = SessionDep):
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

        user = await users_service.find_one_or_none(session=session, filters=UserFilter(email=email))
        if user:
            setup_access_token(user=user)
            return RedirectResponse(f"{settings.oauth2.FRONTEND_HOST}/api/v1/auth/callback")
        else:
            user = UserCreate(email=email, password=None, auth_type="yandex")
            user = await users_service.add(session=session, values=user)
            setup_access_token(user=user)
            return RedirectResponse(f"{settings.oauth2.FRONTEND_HOST}/api/v1/auth/callback")
        
    except OAuthError as e:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    

@router.post("/token-validate")
async def token_validate(token: str | bytes, token_type: str):
    res = await validate_token(token=token, token_type=token_type)
    return res
    

@router.post("/refresh", response_model=TokenInfo, response_model_exclude_none=True)
async def auth_refresh_jwt(
    response: Response, user: UserRead = Depends(get_current_auth_user_for_refresh)
):
    access_token = await setup_access_token(user=user, response=response)

    return TokenInfo(access_token=access_token)


@router.post("/login", response_model=TokenInfo)
async def auth_user_issue_jwt(
    response: Response, user: UserRead = Depends(validate_auth_user)
):
    access_token = await setup_access_token(user=user, response=response)
    refresh_token = await setup_refresh_token(user=user, response=response)

    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.get("/me")
async def auth_user_check_self_info(
    user: UserRead = Depends(get_current_auth_user),
):
    return user

@router.patch("/me", response_model=UserRead)
async def update_me(
    response: Response,
    user_update: UserFilter,
    user: UserRead = Depends(get_current_auth_user),
    session: AsyncSession = SessionDep,
):
    user = await users_service(
        session=session, user=user, user_update=user_update, partial=True
    )
    access_token = await setup_access_token(user=user, response=response)
    refresh_token = await setup_refresh_token(user=user, response=response)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/register")
async def register_user(
    response: Response,
    user: UserLogin,
    session: AsyncSession = SessionDep,
):

    if await users_service.find_one_or_none(session=session, filters=UserFilter(email=user.email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exist",
        )
    # TODO some validation
    user = UserCreate(email=user.email, password=user.password, auth_type="default")
    user = await users_service.add(session=session, values=user)

    access_token = await setup_access_token(user=user, response=response)
    refresh_token = await setup_refresh_token(user=user, response=response)
    
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
async def admin_only():
    return {"message": "This endpoint is accessible only to admins"}

@router.get("/head-only", dependencies=[Depends(require_role("head"))])
async def head_only():
    return {"message": "This endpoint is accessible only to heads"}

@router.get("/student-only", dependencies=[Depends(require_role("student"))])
async def student_only():
    return {"message": "This endpoint is accessible only to students"}