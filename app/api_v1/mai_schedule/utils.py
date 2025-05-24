import hashlib
import json
import logging

import httpx
import redis
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


async def get_group_hash(group_name: str) -> str:
    return f"{hashlib.md5(group_name.encode('utf-8')).hexdigest()}.json"


async def fetch_schedule_from_mai(group_hash: str) -> dict:
    url = f"https://public.mai.ru/schedule/data/{group_hash}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=20)
            logger.info(f"Запрос к {url}, статус: {response.status_code}")

            if response.history:
                logger.warning(f"Редирект: {response.history}")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка HTTP: {e}, response: {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code, detail=e.response.text
            ) from None  # Изменили detail

        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса: {e}")
            raise HTTPException(
                status_code=500, detail=f"Ошибка запроса: {e}"
            ) from None

        except json.JSONDecodeError as e:  # Добавляем явный перехват JSONDecodeError
            logger.error(f"Ошибка декодирования JSON ответа от МАИ: {e}")
            raise HTTPException(
                status_code=500, detail="Некорректный JSON ответ от сервера МАИ"
            ) from None

        except Exception as e:
            logger.exception("Непредвиденная ошибка")
            raise HTTPException(
                status_code=500, detail=f"Непредвиденная ошибка: {e}"
            ) from None
