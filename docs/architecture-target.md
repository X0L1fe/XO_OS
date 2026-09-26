# Целевая архитектура (изолированные модули)

app/
├── main.py               # только создание app, middleware, подключение роутеров, startup/shutdown
├── config.py
├── database/             # db.py, models.py (общая БД на этапе 1)
├── shared/               # общие утилиты (нормализация, исключения, логирование)
│   └── utils.py

├── auth/
│   ├── routes.py         # встроенные эндпоинты /api/auth/*
│   ├── service.py        # бизнес‑логика (регистрация, login, reset и т.д.)
│   └── schemas.py

├── schedule/
│   ├── routes.py         # /api/schedule/*
│   └── service.py        # логика получения расписания, исключений

├── focus/
│   ├── routes.py         # /api/now, /api/focus/* (если понадобится)
│   └── service.py        # start/pause/resume/complete сессий, XP

├── gamification/
│   ├── routes.py         # /api/gamification, /api/settings/gamification
│   └── service.py        # подсчёт XP, уровни, серии

├── stats/
│   ├── routes.py         # /api/stats/*
│   └── service.py        # расчёт семестровой, недельной статистики, топ‑предметов

├── ai/
│   ├── client.py         # обёртка над llama.cpp
│   ├── verification.py   # логика верификации фокуса через ИИ
│   └── routes.py         # /ai/* (если понадобится отдельный эндпоинт)

├── sync/
│   ├── routes.py         # /api/sync/*, /api/google/*, /api/mais/*
│   └── service.py        # импорт ICS/MAIS, синхронизация с Google Calendar, экспорт в Obsidian

├── email/
│   └── service.py        # отправка писем (verification, reset, change)

├── telegram/
│   └── service.py        # обработка web‑хук, генерация кодов привязки

└── events/
    └── service.py        # публикация SSE‑событий (простая обёртка над active_connections)