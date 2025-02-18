from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api_v1 import router as router_v1
from api_v1.websockets import router as websockets_router
from api_v1.sockets import sio_app
from core.config import settings
from contextlib import asynccontextmanager
from core.models import Base, db_helper
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


SECRET_KEY = settings.oauth2.AUTH_SECRET

# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(lifespan=lifespan, root_path="/api")
app.include_router(router=router_v1, prefix="/v1")
app.mount("/", app=sio_app)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
# app.include_router(router=websockets_router)
# app.mount("/", StaticFiles(directory=".", html=True), name="static")


@app.get("/")
async def get():
    return FileResponse("index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
