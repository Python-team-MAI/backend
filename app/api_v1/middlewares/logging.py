from fastapi import FastAPI
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
    
    @app.middleware("http")
    async def authorization(request: Request, call_next):
        if not "Authorization" in request.headers:
            headers = dict(request.headers)
            headers["Authorization"] = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzIiwic3ViIjoiMjEiLCJlbWFpbCI6ImZlZG9ydm9sb3NuZXZAeWFuZGV4LnJ1Iiwicm9sZSI6InN0dWRlbnQiLCJleHAiOjE3NDgyMDMxMTMsImlhdCI6MTc0ODIwMjIxMywianRpIjoiZTdiNmZhYWYtNjNhOC00N2I3LTkyMDAtNTcxZDVlMTdiMzRmIn0.fmcdDe6bgf9Fc9OSPlWUx31wHB1s4Dr7V-WCXTasl2_1OV_ns8EON05BgoaBUCKfMWLcFdQXNC3eYZwcEI58gyTxHs9rQL2cbDg3ykbHSTkN5gPRluab-7hKLIBhyAnoeLT3xOXrolHsE6REkLRdO1ZloItQcKE9ga4gq2dxMMcDgw4Ankm8NFpcX3myHCVHfQcGBufX7pDpllK1GPB6gDKtZm9thZOVmMHoJ0vV5Ao-WWI0QcdCvfPK1RsLwMTvrZPMw9sUkMIT_GaGQUuCw876GFO_-U9fW7JiVGukReNLJbDPP-U8vV5Pnhwa7qNgbNNGgRD1FjgIMRVaQNdonQ"
            request = Request(
            scope=request.scope,
            receive=request.receive,
            send=request._send
            )
            request._headers = headers  # type: ignore
        response = await call_next(request)
        return response