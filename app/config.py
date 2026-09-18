import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("XO_OS_DATABASE_URL", "sqlite:///./data/xo_os.db")
    timezone: str = os.getenv("XO_OS_TIMEZONE", "Europe/Moscow")
    telegram_bot_username: str = "XO_OS_bot"

    # Email settings
    smtp_host: str = os.getenv("XO_OS_SMTP_HOST", "localhost")
    smtp_port: int = int(os.getenv("XO_OS_SMTP_PORT", "587"))
    smtp_username: str | None = os.getenv("XO_OS_SMTP_USERNAME")
    smtp_password: str | None = os.getenv("XO_OS_SMTP_PASSWORD")
    smtp_from_email: str = os.getenv("XO_OS_SMTP_FROM_EMAIL", "noreply@xo-os.local")
    smtp_use_tls: bool = os.getenv("XO_OS_SMTP_USE_TLS", "true").lower() == "true"
    frontend_url: str = os.getenv("XO_OS_FRONTEND_URL", "http://localhost:8000")


settings = Settings()
