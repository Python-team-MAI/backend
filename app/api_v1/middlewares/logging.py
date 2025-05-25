from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request
import time

def register_logging_middler_ware(app: FastAPI):

    @app.middleware('http')
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)

        processing_time = time.time() - start_time
        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time}"
        print(message)
        return response
    
    # @app.middleware("http")
    # async def authorization(request: Request, call_next):
    #     if not "Authorization" in request.headers:
    #         return JSONResponse(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         content="No authorization header",
    #     )
    #     response = await call_next(request)
    #     return response