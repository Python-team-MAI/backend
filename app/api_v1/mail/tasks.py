from app.api_v1.celery.service import celery_app
from .mail import mail, create_message
from asgiref.sync import async_to_sync

@celery_app.task(bind=True, name="send_email")
def send_email(self, recipients: list[str], subject: str, body: str):
    
    message = create_message(
        recipients=recipients, subject=subject, body=body
    )
    async_to_sync(mail.send_message)(message)