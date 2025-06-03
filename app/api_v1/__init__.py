from fastapi import APIRouter
from app.api_v1.chats.view import router as chats_router
from app.api_v1.users.view import router as users_router
from app.api_v1.groups.view import router as groups_router
from app.api_v1.messages.view import router as messages_router
from app.api_v1.offices.view import router as office_router
from app.api_v1.deadlines.view import router as deadlines_router
from app.api_v1.mai_schedule.views import router as schedule_router
from app.api_v1.auth.view import router as demo_jwt_auth_router
from app.api_v1.mail.view import router as mail_router
from app.api_v1.assistant.snapshot_view import router as snapshot_router
from app.api_v1.assistant.assistant_view import router as assistant_router
from app.api_v1.nodes.view import router as nodes_router
from app.api_v1.assistant_chats.view import router as assistant_chats_router
from app.api_v1.assistant_messages.view import router as assistant_messages_router
from app.api_v1.assistant.indexes_view import router as indexes_router

router = APIRouter()
router.include_router(router=demo_jwt_auth_router)
router.include_router(router=mail_router, prefix="/mail")
router.include_router(router=users_router, prefix="/users")
router.include_router(router=chats_router, prefix="/chats")
router.include_router(router=groups_router, prefix="/groups")
router.include_router(router=schedule_router, prefix="/schedule")
router.include_router(router=messages_router, prefix="/messages")
router.include_router(router=office_router, prefix="/offices")
router.include_router(router=deadlines_router, prefix="/deadlines")
router.include_router(router=snapshot_router, prefix="/snapshots")
router.include_router(router=assistant_router, prefix="/assistant")
router.include_router(router=nodes_router, prefix="/nodes")
router.include_router(router=assistant_chats_router, prefix="/assistant-chats")
router.include_router(router=assistant_messages_router, prefix="/assistant-messages")
router.include_router(router=indexes_router, prefix="/indexes")
