from celery import Celery
from celery.app.log import Logging
from app.api_v1.mail.mail import mail, create_message
from asgiref.sync import async_to_sync
from app.core.config import settings

celery_app = Celery("worker", broker=settings.db.BROKER_URL)

celery_app.config_from_object("app.core.config")

@celery_app.task()
def send_email(recipients: list[str], subject: str, body: str):
    
    message = create_message(
        recipients=recipients, subject=subject, body=body
    )
    async_to_sync(mail.send_message)(message)