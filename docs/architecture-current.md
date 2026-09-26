# Текущая архитектура (монолит)

## Основной файл: app/main.py
- Создание FastAPI приложения
- Middleware (CORS, static files)
- Подключение роутеров (инлайн в main.py)
- Инициализация фоновых задач (periodic MAIS check)
- Вспомогательные функции:
  - normalisation categories
  - schedule exclusions
  - event publishing (SSE)
  - экспорт в Obsidian
- Прямые вызовы сервисов:
  - auth.service
  - focus.service
  - sync.service + google_calendar.service
  - email.service
  - telegram.service
  - mais_parser
  - event
  - database, config

## Структура пакетов
app/
├── auth/      # schemas.py, service.py
├── focus/     # routes.py, service.py
├── sync/      # service.py, RESERV.py
├── google_calendar/ # auth.py, service.py
├── ai/        # client.py, verification.py
├── email/     # service.py
├── telegram/  # service.py, schemas.py
├── database/  # db.py, models.py
├── event.py
└── mais_parser.py

## Внешние зависимости
- SQLAlchemy (общая БД)
- Google Calendar API (чрез google_calendar)
- SMTP (email)
- Telegram Bot API
- MAIS API (расписание)
- FastAPI, Uvicorn