from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

reply_kb = ReplyKeyboardMarkup(resize_keyboard=True,
                               keyboard=[[KeyboardButton(text='Выбрать валюту для конвертации')],
                                         [KeyboardButton(text='Инвертировать обмен'),
                                         KeyboardButton(text='Показать все курсы')]])
