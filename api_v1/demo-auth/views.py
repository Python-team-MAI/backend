from fastapi import APIRouter, Depends, HTTPException, Header, Response, Cookie
from typing import Annotated
from fastapi import status
import uuid
from time import time

router = APIRouter(prefix="/demo-auth")

COOKIES = {}
COOKIE_SESSION_ID_KEY = "web-app-session-id"


def generate_session_id() -> str:
    return uuid.uuid4().gex


def get_session_data(session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY)):
    if session_id not in COOKIES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated"
        )
    return COOKIES[session_id]


@router.post("/login-cookie/")
async def demo_auth_login_set_cookie(
    response: Response,
    auth_username: str,
):
    session_id = generate_session_id()
    COOKIES[session_id] = {"username": auth_username, "login_at": int(time())}
    response.set_cookie(COOKIE_SESSION_ID_KEY, session_id)
    return {"result": "ok"}


@router.get("/check-cookie")
async def demo_auth_check_cookie(user_session_data: dict = Depends(get_session_data)):
    pass
