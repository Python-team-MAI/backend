from app.api_v1.users.schemas import UserRead, UserCreate, UserUpdate, UserFilter
from app.api_v1.users.service import users_service
from app.api_v1.users.dependencies import user_by_email
from app.api_v1.auth.helpers import (
    create_access_token,
    create_refresh_token,
    setup_access_token,
    setup_refresh_token,
    set_issue_auth_code,
)
from app.api_v1.auth.validation import (
    http_bearer,
    validate_auth_user,
    get_current_auth_user,
    get_current_auth_user_for_refresh,
    validate_user_email_and_password,
    validate_email,
    validate_password,
)

from app.core.config import settings
from app.core.redis_helper import redis_helper
from app.core.session_manager import SessionDep, TransactionSessionDep
from app.api_v1.mail.mail import mail, create_message
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import (
    TokenInfo,
    UserLogin,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
)
from app.api_v1.mail.tasks import send_email
from .utils import hash_password, create_url_safe_mail_token, decode_url_safe_mail_token
from fastapi import (
    APIRouter,
    Depends,
    Request,
    status,
    HTTPException,
    Body,
    Response,
    Query,
)
from fastapi.responses import JSONResponse
import aiohttp
from .validation import oauth, require_role, validate_token
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis
from authlib.integrations.base_client import OAuthError
from authlib.oauth2.rfc6749 import OAuth2Token
from app.api_v1.utils.setup_logging import setup_logging
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import app.api_v1.auth.utils as auth_utils
from app.api_v1.utils.setup_logging import setup_logging

logger = setup_logging(__name__)

env = Environment(loader=FileSystemLoader("app/templates"))
email_verification_template = env.get_template("email_verification.html")
password_reset_template = env.get_template("reset_password.html")

router = APIRouter(prefix="/auth", tags=["Auth"], dependencies=[Depends(http_bearer)])


GOOGLE_CLIENT_ID = settings.oauth2.AUTH_GOOGLE_ID
GOOGLE_CLIENT_SECRET = settings.oauth2.AUTH_GOOGLE_SECRET
GITHUB_CLIENT_ID = settings.oauth2.AUTH_GITHUB_ID
GITHUB_CLIENT_SECRET = settings.oauth2.AUTH_GITHUB_SECRET
YANDEX_CLIENT_ID = settings.oauth2.AUTH_YANDEX_ID
YANDEX_CLIENT_SECRET = settings.oauth2.AUTH_YANDEX_SECRET
BACKEND_HOST = settings.hosts.BACKEND_HOST
FRONTEND_HOST = settings.hosts.FRONTEND_HOST
GOOGLE_REDIRECT_URI = f"{BACKEND_HOST}/v1/auth/callback/google"
GITHUB_REDIRECT_URI = f"{BACKEND_HOST}/v1/auth/callback/github"
YANDEX_REDIRECT_URI = f"{BACKEND_HOST}/v1/auth/callback/yandex"


@router.get("/google")
async def login_google(request: Request, is_mobile: bool = Query(default=False)):
    return await oauth.google.authorize_redirect(request, GOOGLE_REDIRECT_URI)


@router.get("/callback/google")
async def auth_google(
    response: Response,
    request: Request,
    redis_client=Depends(redis_helper.get_redis_client),
    session: AsyncSession = TransactionSessionDep,
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
    user = await users_service.find_one_or_none(
        session=session, filters=UserFilter(email=email)
    )
    if not user:
        user = UserCreate(
            email=email,
            password=None,
            auth_type="google",
            is_active=True,
            is_superuser=False,
            is_verified=True,
        )
        user = await users_service.add(session=session, values=user)
    async with redis_client as redis:
        code = await set_issue_auth_code(user_id=user.id, redis=redis)

    return RedirectResponse(
        f"{settings.hosts.FRONTEND_HOST}/api/oauth2/finalize?code={code}"
    )


@router.get("/github")
async def login_github(request: Request, is_mobile: bool = Query(default=False)):
    return await oauth.github.authorize_redirect(request, GITHUB_REDIRECT_URI)


@router.get("/callback/github")
async def auth_github(
    response: Response,
    request: Request,
    redis_client: Redis = Depends(redis_helper.get_redis_client),
    session: AsyncSession = TransactionSessionDep,
):
    try:
        token = await oauth.github.authorize_access_token(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не получен.",
            )
        users_resp = await oauth.github.get("https://api.github.com/user", token=token)
        user = users_resp.json()
        email_resp = await oauth.github.get(
            "https://api.github.com/user/emails", token=token
        )
        email = email_resp.json()[0]["email"].lower()
        logger.info(f"Get user email from github: {email}")
        user = await users_service.find_one_or_none(
            session=session, filters=UserFilter(email=email)
        )
        if not user:
            user = UserCreate(email=email, password=None, auth_type="github")
            user = await users_service.add(
                session=session,
                values=user,
                is_active=True,
                is_superuser=False,
                is_verified=True,
            )

        async with redis_client as redis:
            code = await set_issue_auth_code(user_id=user.id, redis=redis)
        return RedirectResponse(
            f"{settings.hosts.FRONTEND_HOST}/api/oauth2/finalize?code={code}"
        )

    except OAuthError as e:
        logger.error(f"Oauth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


@router.get("/yandex")
async def login_github(request: Request, is_mobile: bool = Query(default=False)):
    return await oauth.yandex.authorize_redirect(request, YANDEX_REDIRECT_URI)


@router.get("/callback/yandex")
async def auth_yandex(
    response: Response,
    request: Request,
    redis_client: Redis = Depends(redis_helper.get_redis_client),
    session: AsyncSession = TransactionSessionDep,
):
    try:
        token = await oauth.yandex.authorize_access_token(request)

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не получен.",
            )
        # Получение информации о пользователе
        resp = await oauth.yandex.get("https://login.yandex.ru/info", token=token)
        user_info = resp.json()
        email = user_info["default_email"].lower()
        user = await users_service.find_one_or_none(
            session=session, filters=UserFilter(email=email)
        )
        if not user:
            user = UserCreate(email=email, password=None, auth_type="yandex")
            user = await users_service.add(
                session=session,
                values=user,
                is_active=True,
                is_superuser=False,
                is_verified=True,
            )
        logger.debug(f"User: {user}")
        async with redis_client as redis:
            code = await set_issue_auth_code(user_id=user.id, redis=redis)
        return RedirectResponse(
            f"{settings.hosts.FRONTEND_HOST}/api/oauth2/finalize?code={code}"
        )

    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


@router.post("/oauth2/finalize", response_model=TokenInfo)
async def auth_user_issue_jwt(
    code: str = Query(),
    redis: Redis = Depends(redis_helper.get_redis_client),
    session: AsyncSession = SessionDep,
):
    async with redis as r:
        user_id = await r.get(f"auth_code:{code}")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {user_id} does not exist",
        )

    user_id = user_id.decode("utf-8")
    logger.info(f"Get user_id from redis code {user_id}")
    user = await users_service.get_user_by_id(session=session, id=int(user_id))
    access_token = await setup_access_token(user=user)
    refresh_token = await setup_refresh_token(user=user)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


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
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {user.email} not verified",
        )
    access_token = await setup_access_token(user=user)
    refresh_token = await setup_refresh_token(user=user)

    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/tg-auth")
async def auth_user_issue_jwt(
    tg_id: str = Query(), user_in: UserLogin = Body(), session: AsyncSession = SessionDep
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
    if not user.is_verified:
        raise unverify_exc
    if not auth_utils.validate_password(
        password=user_in.password, hashed_password=user.password
    ):
        raise unauthed_exc
    access_token = await setup_access_token(user=user)
    refresh_token = await setup_refresh_token(user=user)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.mai-students.ru/telegram-webhook/auth",
            data={
                "telegram_id": tg_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
        ) as response:
            ans = await response.text()
    logger.info(f"Ans: {ans}")
    return JSONResponse(content={"success": True}, status_code=200)


@router.get("/me", response_model=UserRead)
async def auth_user_check_self_info(
    user: UserRead = Depends(get_current_auth_user),
):
    return user


@router.patch("/me", response_model=TokenInfo)
async def update_me(
    user_update: UserUpdate,
    user: UserRead = Depends(get_current_auth_user),
    session: AsyncSession = TransactionSessionDep,
):
    await users_service.update(session=session, filters=user, values=user_update)
    access_token = await setup_access_token(user=user)
    refresh_token = await setup_refresh_token(user=user)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.post("/register")
async def register_user(
    response: Response,
    user: UserLogin,
    session: AsyncSession = TransactionSessionDep,
):
    email = user.email
    await validate_user_email_and_password(user=user, session=session)
    user = await users_service.create_new_user(
        session=session, email=email, password=user.password, auth_type="default"
    )
    # mail
    mail_token = create_url_safe_mail_token({"email": email})

    link = f"{settings.hosts.BACKEND_HOST}/v1/auth/verify-mail/{mail_token}"
    html_message = email_verification_template.render(
        link=link, year=datetime.now().year
    )
    subject = "Welcome"
    send_email.delay([email], subject, html_message)
    logger.info(f"Send verified message to email: {email}")
    return {"message": "success"}


@router.get("/verify-mail/{mail_token}")
async def verify_mail(mail_token: str, session: AsyncSession = TransactionSessionDep):
    token_data = decode_url_safe_mail_token(token=mail_token)

    user_email = token_data.get("email", "")

    if user_email:
        user = await users_service.get_user_by_email(session=session, email=user_email)
        logger.debug(
            f"Get user email from mail-token: {user_email}. User exist: {bool(user is not None)}"
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email: {user_email} not found",
            )
        await users_service.set_user_is_verify(session=session, email=user_email)
        logger.info(f"User {user_email} is verified successfully")
        return RedirectResponse(f"{settings.hosts.FRONTEND_HOST}/ru/register/success")

    logger.error(f"Error occured during verification. User email: {user_email}")
    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@router.post("/password-reset-request")
async def password_reset_request(
    email_data: PasswordResetRequestModel, session: AsyncSession = SessionDep
):
    email = email_data.email
    if not validate_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not valid. Domain does not exist",
        )
    user = users_service.get_user_by_email(session=session, email=email)
    if not user:
        return JSONResponse(
            content={"message": f"User with this email does not exist"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # mail
    mail_token = create_url_safe_mail_token({"email": email})

    link = f"{settings.hosts.FRONTEND_HOST}/ru/password/change?token={mail_token}"
    html_message = password_reset_template.render(link=link)
    subject = "Reset password"
    send_email.delay([email], subject, html_message)
    logger.info(f"Send reset password message to email: {email}")
    return JSONResponse(
        content={
            "message": f"Send the reset password message to email if its exist: {email}"
        },
        status_code=status.HTTP_200_OK,
    )


@router.post("/password-reset-confirm/{mail_token}")
async def reset_account_password(
    mail_token: str,
    password_confirm: PasswordResetConfirmModel,
    session: AsyncSession = TransactionSessionDep,
):
    logger.info(f"info: {password_confirm}")
    if password_confirm.new_password != password_confirm.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )
    validate_password(password=password_confirm.new_password)
    logger.debug("Validating password successfully")
    token_data = decode_url_safe_mail_token(token=mail_token)
    user_email = token_data.get("email", "")
    await users_service.reset_user_password(
        session=session, email=user_email, new_password=password_confirm.new_password
    )
    return JSONResponse(
        content={"message": f"Password reset successfully "},
        status_code=status.HTTP_200_OK,
    )
