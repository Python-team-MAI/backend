import time
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.api_v1.utils.setup_logging import setup_logging

logger = setup_logging(__name__)


# Middleware для логирования запросов
class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Логируем входящий запрос
        logger.info(
            "HTTP request started",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "request_id": id(request),
            },
        )

        # Выполняем запрос
        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Логируем ответ
            logger.info(
                "HTTP request completed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "process_time": round(process_time, 4),
                    "request_id": id(request),
                },
            )

            return response

        except Exception as exc:
            process_time = time.time() - start_time

            # Логируем ошибку
            logger.error(
                "HTTP request failed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(exc),
                    "process_time": round(process_time, 4),
                    "request_id": id(request),
                },
                exc_info=True,
            )

            raise exc
