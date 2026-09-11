# XO_OS

Локальная система синхронизации расписания МАИ и основа Personal OS.

## MVP 0.1

Сейчас реализовано:

- импорт `.ics`;
- нормализация событий в модель `Lesson`;
- SQLite + SQLAlchemy;
- стабильная идентификация событий;
- diff между предыдущим и новым расписанием;
- обнаружение `created`, `updated`, `deleted`;
- FastAPI health endpoint;
- CLI для импорта ICS и просмотра diff;
- синхронизация с Google Calendar;
- pytest-тесты.

## Запуск

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Для поддержки Google Calendar также нужны дополнительные зависимости:

```powershell
python -m pip install -e ".[google]"
```

Импорт:

```powershell
xo-os import path\to\schedule.ics
```

Сводка:

```powershell
xo-os status
```

API:

```powershell
uvicorn app.main:app --reload
```

Открой:

`http://127.0.0.1:8765/health`

## Настройка Google Calendar

Для использования синхронизации с Google Calendar необходимо:

1. Перейти в [Google Cloud Console](https://console.cloud.google.com/)
2. Создать новый проект или выбрать существующий
3. Включить API Google Calendar для проекта
4. Учетные данные → Создать учетные данные → ID клиента OAuth
   - Тип приложения: Пользовательское приложение для настольных компьютеров
   - Скачать полученный JSON-файл и сохранить его как `client_secret.json` в корне проекта
5. При первом запуске синхронизации откроется браузер для авторизации в Google аккаунте
6. После авторизации токен будет сохранен в файле `token.json` (по умолчанию в директории `./data/`)

## Архитектура

`ICS -> parser -> normalized lesson -> SQLite -> diff`

Google Calendar, Obsidian, scheduler и gamification будут подключаться поверх локальной БД, а не напрямую к ICS.
