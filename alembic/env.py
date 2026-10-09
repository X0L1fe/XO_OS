from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# --- Добавляем корень проекта в sys.path ---
# Это нужно, чтобы `from app.config import settings` и
# `from app.database.models import Base` работали при запуске
# `alembic` из корня проекта.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings  # noqa: E402
from app.database.models import Base  # noqa: E402

# Alembic Config объект
config = context.config

# Подсовываем URL из настроек приложения
config.set_main_option("sqlalchemy.url", settings.database_url)

# Логирование из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные для autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Оффлайн-режим: только генерация SQL, без подключения."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # ловим изменения типов колонок
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Онлайн-режим: подключаемся к реальной БД."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True,  # ВАЖНО для SQLite: ALTER через batch
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
