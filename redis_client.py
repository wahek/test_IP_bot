import asyncio
import json

from redis import asyncio as aioredis
from config import settings


class RedisClient:
    """
    Класс для работы с radis
    Использовать, как контекстный менеджер
    """

    def __init__(self):
        self.redis: aioredis.Redis | None = None
        self.redis_url: str = settings.redis

    async def __connect(self):
        self.redis = aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)

    async def get(self, key) -> dict:
        """Получение данных по ключу (json)"""

        return json.loads(await self.redis.get(key))

    async def mget(self, keys: list | set) -> list[str]:
        """Получение списка значений по списку ключей"""

        return await self.redis.mget(*keys)

    async def get_valute(self, key) -> list:
        """Получение списка имеющихся ключей валют"""

        a = await self.redis.sinter(key)
        return a

    async def set_data(self, data: list[dict]) -> None:
        """Занесение валют в redis | Ключ: {CharCode: ..., Name: ..., Value: ...}"""

        async with self.redis.pipeline() as pipe:
            for item in data:
                for key, value in item.items():
                    value_str = json.dumps(value)
                    await pipe.set(key, value_str)
            await pipe.execute()

    async def set_keys(self, data: dict) -> None:
        """Занесение списка имеющихся ключей в redis"""

        async with self.redis.pipeline() as pipe:
            key = next(iter(data))
            await pipe.delete(key)
            for item in data.values():
                for v in item:
                    await pipe.sadd(key, v)
            await pipe.execute()

    async def set_user(self, user_id) -> None:
        """
        Добавление пользователя в Redis
        default: {'valute': 'USD', 'invert': 1}
        """

        await self.redis.set(user_id, json.dumps({'valute': 'USD', 'invert': 1}), ex=604800)

    async def user_invert(self, user_id) -> bool:
        """Изменение параметра инверсии конвертации"""

        data = await self.get(user_id)
        data['invert'] = 1 if data['invert'] == 0 else 0
        await self.redis.set(user_id, json.dumps(data), ex=604800)
        return data['invert']

    async def user_currency(self, user_id, currency) -> None:
        """Изменение выбранной валюты у пользователя"""

        try:
            data = await self.get(user_id)
        except TypeError:
            await self.set_user(user_id)
            data = await self.get(user_id)
        print(data)
        data['valute'] = currency
        print(data)
        await self.redis.set(user_id, json.dumps(data), ex=604800)

    async def __aenter__(self):
        await self.__connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.redis.aclose()


