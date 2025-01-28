from fastapi import APIRouter
from .chats.views import router as chats_router
from .users.views import router as users_router
from .groups.views import router as groups_router

router = APIRouter()
router.include_router(router=chats_router, prefix="/chats")
router.include_router(router=users_router, prefix="/users")
router.include_router(router=groups_router, prefix="/groups")

