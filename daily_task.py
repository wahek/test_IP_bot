import asyncio
import logging
from datetime import datetime, timedelta


class DeferredTask:
    """
    Класс для выполнения задач по расписанию
    Выполнение 1 ращ в день
    """

    FREQUENCY_UPDATE = 10  # 1 day (seconds)

    def __init__(self, daily_task: callable):
        self.daily_task: callable = daily_task

    async def daily_update_valute(self):
        """Запуск цикла обновления данных"""

        task = asyncio.create_task(self.job())
        await task

    async def job(self, hour=18, minute=0):
        """
        Расписание выполнения задач
        При запуске, затем в выбранное время(utc), затем каждые 24 часа
        """
        await self.daily_task()
        logging.info("Данные обновлены")
        now = datetime.utcnow()
        next_run = datetime.combine(now.date(), datetime.min.time()) + timedelta(hours=hour, minutes=minute)
        if next_run <= now:
            next_run += timedelta(days=1)

        wait_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        while True:
            logging.info("Данные обновлены")
            await self.daily_task()
            await asyncio.sleep(self.FREQUENCY_UPDATE)
