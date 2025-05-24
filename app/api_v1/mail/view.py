from fastapi import APIRouter, HTTPException, status, Depends
import logging
from app.api_v1.auth.view import get_current_auth_user, email_verification_template, password_reset_template
from app.api_v1.auth.validation import require_superuser
from app.api_v1.auth.utils import create_url_safe_mail_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.session_manager import SessionDep, TransactionSessionDep
from .mail import create_message, mail
from .schemas import SendMailModel
from datetime import datetime
from app.core.config import settings
from app.api_v1.celery_tasks import send_email


router = APIRouter(
    tags=["Mail"],
    dependencies=[Depends(get_current_auth_user), Depends(require_superuser())],
)


@router.post("/send-mail")
async def send_mail(mail: SendMailModel):
    emails = mail.addresses

    subject = mail.subject
    message = mail.message
    if len(emails) == 1:

        if message == "email_verification":
            mail_token = create_url_safe_mail_token({"email": emails[0]})
            link = f"{settings.hosts.BACKEND_HOST}/api/v1/auth/verify-mail/{mail_token}"
            message = email_verification_template.render(link=link, year=datetime.now().year)

        elif message == "reset_password":
            mail_token = create_url_safe_mail_token({"email": emails[0]})
            link = (
                f"{settings.hosts.BACKEND_HOST}/api/v1/auth/password-reset-confirm/{mail_token}"
            )
            message = password_reset_template.render(link=link)

    send_email.delay(emails, subject, message)

    return {"message": "Email sent successfully"}
