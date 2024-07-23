import asyncio
import logging
import sys
from os import getenv
from config import settings

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
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
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}!\n"
                         f"Бот умеет конвертировать валюты в рубли и наоборот\n"
                         f" \n"
                         f"Для вывода курсов всех валют введите команду /rates\n"
                         f" \n"
                         f"Для выбора валюты для конвертации введите команду /currencies\n"
                         f" \n"
                         f"Для инверсии конвертации введите команду /invert", reply_markup=reply.reply_kb)
    async with RedisClient() as redis:
        await redis.set_user(message.from_user.id)


@dp.message(Command('currencies'))
@dp.message(F.text == 'Выбрать валюту для конвертации')
async def choice_currency(message: Message) -> None:
    await message.answer(text='Выберете валюту для конвертации\n'
                              'Основные валюты:', reply_markup=await inline.major_currencies())
    await message.answer(text='Дополнительные валюты', reply_markup=await inline.currencies())


@dp.message(Command('invert'))
@dp.message(F.text == 'Инвертировать обмен')
async def invert (message: Message) -> None:
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
    await message.answer(text=f'\n'.join(await StringForAiogram.get_all_course()))



@dp.callback_query(F.data.startswith('currency_'))
async def pick_currency(callback: CallbackQuery) -> None:
    valute = callback.data.replace('currency_', '')
    await callback.answer(f'Вы выбрали: {valute}')
    await callback.message.answer(text='Валюта выбрана, введите количество для конвертации в чат')


@dp.message(Command('rates'))
async def echo_handler(message: Message) -> None:
    await message.answer(text='Выберете валюту для конвертации', reply_markup=await inline.currencies())


async def on_startup() -> None:
    client = HTTPClient()
    redis_client = RedisClient()
    try:
        data = await client.get_data()
        async with redis_client as redis:
            await redis.set_data(data)
            print(client.keys)
            await redis.set_keys(client.keys)
    finally:
        await client.close()


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
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
