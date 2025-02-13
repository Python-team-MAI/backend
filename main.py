from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api_v1 import router as router_v1
from api_v1.websockets import router as websockets_router
from api_v1.sockets import sio_app
from contextlib import asynccontextmanager
from core.models import Base, db_helper
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=router_v1, prefix="/api/v1")
app.mount("/", app=sio_app)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.include_router(router=websockets_router)
# app.mount("/", StaticFiles(directory=".", html=True), name="static")


@app.get("/")
async def get():
    return FileResponse("index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
