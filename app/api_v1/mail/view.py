from fastapi import APIRouter, HTTPException, status, Depends
import logging
from app.api_v1.auth.view import get_current_auth_user
from app.api_v1.auth.validation import require_superuser
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session_manager import SessionDep, TransactionSessionDep
from .mail import create_message, mail
from .schemas import EmailCreate



router = APIRouter(tags=["Mail"], dependencies=[Depends(get_current_auth_user), Depends(require_superuser())])


@router.post("/send-mail")
async def send_mail(email: EmailCreate):
    emails = email.addresses

    html = "<h1>Welcome to the app<h1>"
    message = create_message(recipients=emails, subject="Welcome", body=html)

    await mail.send_message(message)
    return {"message": "Email sent successfully"}
