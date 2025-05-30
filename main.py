from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from app.api_v1 import router as router_v1
from app.api_v1.sockets.sockets import sio_app
from app.core.config import settings
from contextlib import asynccontextmanager
from app.core.base.base_model import Base
from app.api_v1.utils.setup_logging import setup_logging
from starlette.config import Config
from typing import AsyncGenerator
from authlib.integrations.starlette_client import OAuth
from app.api_v1.middlewares.logging import LoggingMiddleware
import uvicorn
from pathlib import Path

logger = setup_logging(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:
    global logger
    """
    Управляет жизненным циклом планировщика приложения.

    Args:
        app (FastAPI): Экземпляр приложения FastAPI.
    """

    logger.info("Начало работы приложения...")
    yield
    logger.info("Завершение работы приложения...")


def create_app() -> FastAPI:
    """
    Создание и конфигурация FastAPI приложения.

    Returns:
        Сконфигурированное приложение FastAPI
    """
    SECRET_KEY = settings.oauth2.AUTH_SECRET
    app = FastAPI(
        title="MAI API",
        description=("python project"),
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://mai-students.ru"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
    # register_logging_middler_ware(app)
    register_routers(app)

    return app


def register_routers(app: FastAPI) -> None:
    """Регистрация роутеров приложения."""

    root_router = APIRouter()

    @app.get("/")
    def home_page():
        logger.info("Обращение к главной странице", extra={"endpoint": "/"})
        return {"message": "Hello from MAI API"}

    @app.get("/health")
    def health_check():
        logger.info("Health check запрос", extra={"endpoint": "/health"})
        return {"status": "healthy", "service": "mai-api"}

    app.include_router(router=router_v1, prefix="/v1")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.mount("/", app=sio_app)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="MAI API",
        version="1.0.0",
        description="это жесть короче",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # Это по умолчанию для всех методов
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = create_app()
app.openapi = custom_openapi


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=1)
