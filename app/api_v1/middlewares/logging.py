from fastapi import FastAPI
from fastapi.requests import Request
import time
from app.api_v1.utils.setup_logging import setup_logging

logger = setup_logging()

def register_logging_middler_ware(app: FastAPI):

    @app.middleware('http')
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        print("before", start_time)
        response = await call_next(request)

        processing_time = time.time() - start_time
        print("processed after", processing_time)
        return response