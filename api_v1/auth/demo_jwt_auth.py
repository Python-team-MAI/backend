from api_v1.users.schemas import User
from api_v1.auth.helpers import create_access_token, create_refresh_token
from api_v1.auth.validation import http_bearer, validate_auth_user, get_current_auth_user, get_current_auth_user_for_refresh
from .schemas import TokenInfo
from fastapi import APIRouter, Depends 
from fastapi.security import (
    OAuth2PasswordRequestForm
)
import logging
import api_v1.auth.utils as auth_utils

router = APIRouter(prefix="/jwt", tags=["JWT"], dependencies=[Depends(http_bearer)])



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
