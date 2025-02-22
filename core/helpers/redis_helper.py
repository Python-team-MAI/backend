from redis.asyncio import Redis
from core.config import settings
from contextlib import asynccontextmanager

class RedisHelper:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.r = None  # Клиент будет создан при первом использовании

    @asynccontextmanager
    async def get_redis_client(self):
        if self.r is None:
            self.r = Redis(host=self.host, port=self.port, db=self.db)
        try:
            await self.r.ping()  # Проверяем подключение
            yield self.r
        except Exception as e:
            print(f"Ошибка подключения к Redis: {e}")
            raise

redis_helper = RedisHelper(host=settings.db.REDIS_HOST, port=settings.db.REDIS_PORT, db=settings.db.REDIS_DB)
