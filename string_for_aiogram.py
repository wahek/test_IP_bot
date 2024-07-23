from redis_client import RedisClient

class StringForAiogram:
    @staticmethod
    async def get_all_course() -> list[str]:
        string_list = []
        async with RedisClient() as redis:
            keys = await redis.get_valute('valute')
            data = await redis.mget(keys)
            for item in data:
                string_list.append(f'{item.CharCode} ({item.Name}) -> {item.Value} RUB (Российский рубль)')
        return string_list
