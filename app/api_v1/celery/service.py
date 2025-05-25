from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "app",
    broker=settings.db.CELERY_BROKER_URL,
    backend=settings.db.CELERY_RESULT_URL,
    include=["app.api_v1.assistant.tasks", "app.api_v1.mail.tasks"],  # все модули с тасками
)

# # настройки можно указать явно
# celery_app.conf.update(
#     task_serializer="json",
#     result_serializer="json",
#     accept_content=["json"],
#     timezone="UTC",
#     enable_utc=True,
#     task_track_started=True,
#     task_time_limit=300,  # fail-safe таймаут
#     task_soft_time_limit=270,
# )