import asyncio

from redis import asyncio as aioredis
from config import settings


async def get_redis_session():
    redis = RedisClient()
    async with redis:
        print(await redis.get("usd"))


class RedisClient:
    def __init__(self):
        self.redis = None
        self.redis_url = settings.redis

    async def __connect(self):
        self.redis = aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)

    async def get(self, key):
        return await self.redis.get(key)



    async def __aenter__(self):
        await self.__connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.redis.aclose()


