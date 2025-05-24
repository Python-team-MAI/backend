from fastapi import FastAPI
from fastapi.requests import Request
import time
from app.api_v1.utils.setup_logging import setup_logging

logger = setup_logging()

def register_logging_middler_ware(app: FastAPI):

    @app.middleware('http')
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)

        processing_time = time.time() - start_time
        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time}"
        print(message)
        return response