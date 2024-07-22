import asyncio
import json

from redis import asyncio as aioredis
from config import settings


class RedisClient:
    def __init__(self):
        self.redis: aioredis.Redis | None = None
        self.redis_url: str = settings.redis

    async def __connect(self):
        self.redis = aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)

    async def get(self, key):
        return json.loads(await self.redis.get(key))

    async def set_data(self, data: list[dict]):
        print('start')
        async with self.redis.pipeline() as pipe:
            for item in data:
                for key, value in item.items():
                    value_str = json.dumps(value)
                    await pipe.set(key, value_str)
            await pipe.execute()
            print('ok')

    async def set_keys(self, data: dict):
        async with self.redis.pipeline() as pipe:
            key = next(iter(data))
            await pipe.delete(key)
            for item in data.values():
                for v in item:
                    print(v)
                    await pipe.sadd(key, v)
            await pipe.execute()
            print('okk')

    async def __aenter__(self):
        await self.__connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.redis.aclose()


if __name__ == '__main__':
    async def main():
        async with RedisClient() as redis:
            await redis.set_keys({5: {6, 7, 8, 9}})
            # print(await redis.get('5'))


    asyncio.run(main())
