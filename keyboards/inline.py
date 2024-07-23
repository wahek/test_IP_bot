from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from redis_client import RedisClient

VALUTE = 'valute'
MAJOR_VALUTE = {'USD', 'EUR', 'CNY'}


async def major_currencies() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    async with RedisClient() as redis:
        for item in await redis.get_valute(VALUTE) & MAJOR_VALUTE:
            kb.add(InlineKeyboardButton(text=f'{item}', callback_data=f'currency_{item}'))
    return kb.adjust(1).as_markup()


async def currencies() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    async with RedisClient() as redis:
        for item in sorted(list(await redis.get_valute(VALUTE)-MAJOR_VALUTE)):
            kb.add(InlineKeyboardButton(text=f'{item}', callback_data=f'currency_{item}'))
    return kb.adjust(3).as_markup()
