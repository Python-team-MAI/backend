from fastapi import APIRouter
from app.api_v1.chats.view import router as chats_router
from app.api_v1.users.view import router as users_router
from app.api_v1.groups.view import router as groups_router
from app.api_v1.mai_schedule.views import router as schedule_router
from app.api_v1.auth.demo_jwt_auth import router as demo_jwt_auth_router

router = APIRouter()
router.include_router(router=chats_router, prefix="/chats")
router.include_router(router=users_router, prefix="/users")
router.include_router(router=groups_router, prefix="/groups")
router.include_router(router=schedule_router, prefix="/schedule")
router.include_router(router=demo_jwt_auth_router)
