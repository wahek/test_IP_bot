### Если с докером проблемы:
- > устанавливаем зависимости:
  > > __pip install -r requirements.txt__
- > Добавляем переменные окружения __.env__:
  > > - __BOT_TOKEN__
  > > - __REDIS__
- > Запускаем __main.py__
  
___

### О проекте:
Telegram бот для предоставления актуальных курсов валют с сайта ЦБ РФ.

Конвертация проводится в рублях. Есть опция конвертации, как в одну, так и в другую сторону.

Реализованы удобные клавиатуры для выбора валют.

Курсы, и пользователи хранятся в redis.