from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings():
    database_url: str = os.getenv(
        "XO_OS_DATABASE_URL", "sqlite:///./data/xo_os.db"
    )
    timezone: str = os.getenv("XO_OS_TIMEZONE", "Europe/Moscow")
    telegram_bot_username: str = "XO_OS_bot"


settings = Settings()
