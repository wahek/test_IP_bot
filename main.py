import asyncio
import logging
import sys
import time
from os import getenv
from config import settings
import re

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from daily_task import DeferredTask
from redis_client import RedisClient
from requests import HTTPClient
from string_for_aiogram import StringForAiogram

from keyboards import inline
from keyboards import reply

TOKEN = settings.bot_token

dp = Dispatcher()


@dp.message(Command(commands=['start', 'help']))
async def command_start_handler(message: Message) -> None:
    """Запуск бота"""
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}!\n"
                         f"Бот умеет конвертировать валюты в рубли и наоборот\n"
                         f" \n"
                         f"Для вывода курсов всех валют введите команду /rates\n"
                         f" \n"
                         f"Для выбора валюты для конвертации введите команду /currencies\n"
                         f" \n"
                         f"Для инверсии конвертации введите команду /invert", reply_markup=reply.reply_kb)
    if 'start' in message.text:
        async with RedisClient() as redis:
            await redis.set_user(message.from_user.id)


@dp.message(Command('currencies'))
@dp.message(F.text == 'Выбрать валюту для конвертации')
async def choice_currency(message: Message) -> None:
    await message.answer(text='Дополнительные валюты:', reply_markup=await inline.currencies())
    await message.answer(text='Выберете валюту для конвертации\n'
                              'Основные валюты:', reply_markup=await inline.major_currencies())


@dp.message(Command('invert'))
@dp.message(F.text == 'Инвертировать обмен')
async def invert(message: Message) -> None:
    async with RedisClient() as redis:
        try:
            user_invert = await redis.user_invert(message.from_user.id)
        except TypeError:
            await redis.set_user(message.from_user.id)
            user_invert = await redis.user_invert(message.from_user.id)
        if user_invert:
            await message.answer(text='Конвертация рублей в выбранную валюту')
        else:
            await message.answer(text='Конвертация выбранной валюты в рубли')


@dp.message(Command('rates'))
@dp.message(F.text == 'Показать все курсы')
async def rates(message: Message) -> None:
    try:
        await message.answer(text=f'\n'.join(await StringForAiogram.get_all_course()))
    except UnboundLocalError:
        await message.answer(text='Сбой данных, подождите... Бот перезапускается')
        await DeferredTask(on_startup).daily_update_valute()


@dp.callback_query(F.data.startswith('currency_'))
async def pick_currency(callback: CallbackQuery) -> None:
    valute = callback.data.replace('currency_', '')
    await callback.answer(f'Вы выбрали: {valute}')
    async with RedisClient() as redis:
        v_name = await redis.get(valute)
        await redis.user_currency(callback.from_user.id, v_name['CharCode'])
    await callback.message.answer(text=f'Выбрано: {v_name["Name"]}. Введите количество для конвертации в чат')


@dp.message(Command('rates'))
async def echo_handler(message: Message) -> None:
    await message.answer(text='Выберете валюту для конвертации', reply_markup=await inline.currencies())


@dp.message()
async def convert(message: Message) -> None:
    string = StringForAiogram()
    await message.answer(text=await string.convert(user_id=message.from_user.id, string=message.text))


async def on_startup() -> None:
    """Создание отложенной задачи для обновления курса валют"""

    client = HTTPClient()
    redis_client = RedisClient()
    try:
        data = await client.get_data()
        async with redis_client as redis:
            await redis.set_data(data)
            await redis.set_keys(client.keys)
    finally:
        await client.close()


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await asyncio.gather(
        DeferredTask(on_startup).daily_update_valute(),
        dp.start_polling(bot)
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('STOP')

