
import json
from .utils import logger, get_group_hash, fetch_schedule_from_mai
from redis import asyncio as redis
from core.config import settings
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import datetime
from core.helpers import redis_helper


router = APIRouter(tags=["Shedule"])


@router.get("/{group_name}")
async def get_schedule(
    group_name: str, redis_client: redis.Redis = Depends(redis_helper.get_redis_client)
):
    group_hash = await get_group_hash(group_name)
    cache_key = f"schedule:{group_hash}"


    # Проверяем Redis
    try:
        async with redis_client as r:
            cached_schedule = await r.get(cache_key)

        if cached_schedule:
            logger.info(f"Расписание для {group_name} взято из Redis")
            return JSONResponse(content=json.loads(cached_schedule))
    except Exception as e:
        logger.error(f"Ошибка при чтении из Redis: {e}")

    # Получаем с МАИ
    try:
        schedule_data = await fetch_schedule_from_mai(group_hash)

        if not schedule_data:
            logger.info(f"Расписание для {group_name} не найдено на сервере МАИ.")
            raise HTTPException(
                status_code=404, detail="Schedule not found"
            )  # corrected detail message

        try:
            async with redis_client as r:
                await r.set(cache_key, json.dumps(schedule_data), ex=datetime.timedelta(days=settings.db.EXPIRE_TIME_DAYS).total_seconds())
            logger.info(f"Расписание для {group_name} сохранено в Redis")
        except Exception as e:
            logger.warning(f"Не удалось сохранить расписание в Redis: {e}")

        return schedule_data

    except HTTPException as e:
        logger.error(
            f"Ошибка при получении расписания для группы {group_name}: {e.detail}"
        )
        raise 