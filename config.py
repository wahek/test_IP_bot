from os import getenv
from dotenv import load_dotenv


class Settings:

    def __init__(self):
        load_dotenv()
        self.bot_token: str = getenv("BOT_TOKEN")
        self.redis: str = getenv("REDIS")


settings = Settings()

