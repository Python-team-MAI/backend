from fastapi import APIRouter, Depends
from celery.result import AsyncResult
from app.api_v1.auth.validation import require_superuser

router = APIRouter(tags=["Celery Tasks"], dependencies=[Depends(require_superuser())])


@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """
    Получить статус celery-задачи по task_id
    """
    result = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": result.status,  # PENDING | STARTED | SUCCESS | FAILURE | RETRY
    }

    if result.status == "SUCCESS":
        response["result"] = result.result
    elif result.status == "FAILURE":
        response["error"] = str(result.result)

    return response
