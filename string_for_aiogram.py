import json
from decimal import Decimal, getcontext

from aiogram import html
from redis_client import RedisClient
from daily_task import DeferredTask

getcontext().prec = 4

class StringForAiogram:
    @staticmethod
    async def get_all_course() -> list[str]:
        string_list = []
        async with RedisClient() as redis:
            try:
                keys = await redis.get_valute('valute')
                data = await redis.mget(keys)
            except TypeError:
                pass
            for item in data:
                item = json.loads(item)
                string_list.append(f'{html.bold("RUB")} {html.bold(item["Value"])} => {html.bold(item["CharCode"])} - '
                                   f'({item["Name"]})')
        return string_list

    async def calculate_exchange(self, user_id: int, value: float) -> str:
        async with RedisClient() as redis:
            try:
                valute: dict = await redis.get(user_id)
            except TypeError:
                await redis.set_user(user_id)
                valute = await redis.get(user_id)
            current_valute = await redis.get(valute['valute'])
            result = await self.__invert_exchange(float(current_valute['Value'].replace(',', '.')),
                                                  bool(valute['invert']), value)
            print(bool(valute['invert']))
            if bool(valute['invert']):
                return f'{html.bold(value)} {html.bold("RUB")} => ' \
                       f'{html.bold(result)} {html.bold(valute["valute"])} ({current_valute["Name"]})'
            else:
                return f'({current_valute["Name"]}) {html.bold(value)} {html.bold(valute["valute"])} => ' \
                       f'{html.bold(result)} {html.bold("RUB")}'

    async def convert(self, user_id: int, string: str) -> str:
        try:
            string = float(string)
            return await self.calculate_exchange(user_id, string)
        except ValueError:
            return 'Бот принимает только цифры для конвертации (ввод дробных чисел через точку 86.1)\n' \
                   'Либо введена неверная команда, воспользуйтесь кнопками клавиатуры или /help'

    @staticmethod
    async def __invert_exchange(coast: float, invert: bool, value: float) -> float:
        if invert:
            return float(Decimal(value) / Decimal(coast))
        else:
            if value == 0:
                return 0
            return coast * value
