**Анализ файла `app/main.py`**

---

### Таблица блоков main.py

| участок main.py | назначение | текущие зависимости | целевой модуль/файл | уже существует? | риск переноса |
|-----------------|------------|---------------------|---------------------|-----------------|---------------|
| **Импорты (стр. 1‑118)** | Подгрузка всех необходимых пакетов и внутренних модулей | `*` (весь импорт‑блок) | `app/main.py` (оставить как central импорт‑хуб) | Да | Низкий (импорты нужны всему файлу) |
| **Настройка логгирования (стр. 22‑33)** | Конфигурация базового логгера и подавление шума от сторонних библиотек | `logging`, `httpx`, `httpcore`, `urllib3` | `app/logging_config.py` (новый модуль) | Нет | Низкий (изолирован) |
| **Создание FastAPI‑приложения и CORS‑middleware (стр. 137‑152)** | Инициализация объекта `app`, добавление CORS | `FastAPI`, `CORSMiddleware`, `Settings` | `app/app_factory.py` (фабрика создания приложения) | Нет | Средний (нужен доступ к `settings` и `app`) |
| **Монтирование статических файлов (стр. 152)** | Раздача файлов из `app/web/static` | `StaticFiles`, `Path` | `app/app_factory.py` (рядом с созданием приложения) | Нет | Низкий |
| **Инициализация БД и настроек (стр. 154‑158)** | Создание singleton‑объектов `db` и `settings` | `Database`, `Settings` | `app/core.py` (общие зависимости) | Нет (аналогичные объекты есть в `app/database/db.py` и `app/config.py`, но синглтоны здесь) | Средний (модули могут импортировать эти объекты) |
| **Подключение роутеров (стр. 163‑166)** | Регистрация уже существующих роутеров (stats, gamification, focus, schedule) | `app.stats.router`, `app.gamification.router`, `app.focus.router`, `app.schedule.router` | Оставить в `app/main.py` (точка регистрации) | Да | Низкий |
| **Dev‑only комментарий о сбросе gamification (стр. 168‑171)** | Заглушка для будущего кода | — | Удалить или перенести в скрипт разработки | Нет | Низкий |
| **Webhook Telegram (стр. 173‑189)** | Прием обновлений от Telegram Bot API | `Request`, `BackgroundTasks`, `telegram_bot_app` (глобальная, импортируется позже) | `app/telegram/routes.py` (новый файл) | Нет (веб‑хуки пока только здесь) | Средний (зависит от фоновой задачи и глобального `telegram_bot_app`) |
| **Функции работы с Obsidian‑путем (стр. 191‑205)** | Чтение/запись пути к хранилищу Obsidian из файла и env | `Path`, `json`, `os` | `app/obsidian/utils.py` (или `app/obsidian/service.py`) | Нет | Низкий (чистые утилиты) |
| **Проверка наличия frontend‑директории (стр. 207‑212)** | Определение, существует ли каталог с фронтендом для SPA | `Path` | `app/static.py` (или оставить в `app_factory.py`) | Нет | Низкий |
| **Маршрут /api/health (стр. 214‑218)** | Простейший здоровье‑чек | `fastapi` (только декоратор) | `app/core/routes.py` (или оставить в main) | Нет | Низкий |
| **Маршрут /api/export (стр. 220‑245)** | Экспорт уроков в Obsidian | `User`, `Depends`, `BackgroundTasks`, `SyncService`, `get_obsidian_vault_path`, `os.getenv` | `app/obsidian/routes.py` | Нет | Средний (зависит от сервиса и хелперов) |
| **Блок авторизации (регистрация, верификация, логин, logout, info, status) (стр. 247‑510)** | Все эндпоинты /api/auth/* | `UserCreate`, `UserLogin`, `AuthStatusResponse`, `email_service`, `db`, `settings`, `secrets`, `jwt`? (фактически используется сессия через cookie) | `app/auth/routes.py` (создать) | Нет (сервис и схемы есть, но роутов нет) | Средний (требует импорта сервиса и настроек) |
| **Блок сброса пароля и смены email (стр. 515‑682)** | Эндпоинты инициации и подтверждения сброса пароля и смены email | `User`, `Depends`, `email_service`, `settings`, `secrets`, `token`‑функции из сервиса auth | `app/auth/routes.py` (дополнить) | Нет | Средний |
| **Маршрут /api/events (стр. 687‑699)** | SSE‑канал для реального времени | `Request`, `Depends`, `StreamingResponse`, `event_publisher` | `app/core/routes.py` (или оставить в main) | Нет | Низкий |
| **Маршрут /api/now (стр. 701‑812)** | Возвращает текущее состояние NowBlock (фокус/урок/idle) | `User`, `Depends`, `FocusService`, `msk_now_naive`, `timedelta`, `get_schedule_exclusions`, `lesson_is_visible`, `normalize_schedule_category`, `_calculate_elapsed_seconds` | `app/focus/routes.py` (логически относится к фокусу) | Да (фокус‑роутер уже есть) | Низкий (можно переместить) |
| **Маршрут /api/achievements (стр. 819‑853)** | Список достижений на основе статистики | `User`, `Depends`, `UserStats` | `app/stats/routes.py` (статистический роутер) | Да | Низкий |
| **Маршрут /api/calendar/status (стр. 855‑880)** | Статус подключения к Google Calendar | `GOOGLE_OAUTH_AVAILABLE`, `get_token_path`, `os.path.exists`, `Credentials`, `Request` | `app/google_calendar/routes.py` (или `app/google_calendar/service.py`) | Нет | Средний |
| **Маршруты Obsidian статуса и пути (стр. 882‑915)** | Получение/установка пути к хранилищу Obsidian | `User`, `Depends`, `get_obsidian_vault_path`, `save_obsidian_vault_path`, `os.getenv` | `app/obsidian/routes.py` | Нет | Низкий |
| **Маршруты MAIS groups / import / set‑group (стр. 917‑988)** | Получение списка групп, импорт расписания, привязка группы к пользователю | `User`, `Depends`, `fetch_groups`, `fetch_group_schedule`, `parse_mais_schedule`, `SyncService`, `GoogleCalendarSyncService` (опционально) | `app/mais/routes.py` (или `app/mais/service.py`) | Нет | Средний (зависит от сервиса синхронизации) |
| **Маршруты Google OAuth (календари, onboarding, select, auth, callback, status, disconnect) (стр. 990‑1228)** | Весь flow работы с Google Calendar | `User`, `Depends`, `GOOGLE_OAUTH_AVAILABLE`, `get_credentials_path`, `get_token_path`, `SCOPES`, `Flow`, `Credentials`, `Request`, `RedirectResponse`, `httpx` (внутри сервиса) | `app/google_calendar/routes.py` | Нет | Средний‑высокий (много локальной логики и зависимостей от настроек) |
| **Маршрут /api/debug/echo (стр. 1230‑1238)** | Отладка: эхо‑ответ с телом запроса | `Request` | `app/core/routes.py` (debug‑роут) | Нет | Низкий |
| **Маршрут /api/mais/import_get (стр. 1240‑1244)** | Тестовый эндпоинт (возвращает имя группы) | `str` | Удалить (дублирует функционал) | Нет | Низкий |
| **Маршруты Telegram link/status/unlink (стр. 1251‑1325)** | Управление привязкой Telegram‑аккаунта | `User`, `Depends`, `create_telegram_link_code`, `unlink_telegram_account`, `Settings.telegram_bot_username` | `app/telegram/routes.py` | Нет | Низкий |
| **Маршруты уведомлений (стр. 1328‑1394)** | Получение, пометка как прочитанное, переключение_enabled | `User`, `Depends`, `Notification` | `app/notifications/routes.py` | Нет | Низкий |
| **Фоновая проверка MAIS‑расписания (стр. 1400‑1485)** | Проверка изменений расписания для конкретного пользователя | `User`, `Session`, `async_fetch_group_schedule`, `parse_mais_schedule`, `SyncService`, `GoogleCalendarSyncService`, `Notification`, `httpx` (для Telegram) | `app/sync/tasks.py` (или `app/mais/tasks.py`) | Нет | Средний (зависит от сервисов и БД) |
| **Периодическая фоновая задача (стр. 1487‑1540)** | Запускает проверку для всех пользователей с заданным интервалом | `asyncio`, `utc_now`, `timezone`, `User`, `Session` | `app/sync/tasks.py` | Нет | Средний |
| **Старт фоновой задачи при стартапе (стр. 1543‑1546)** | Регистрация `periodic_mais_check` в цикле событий FastAPI | `asyncio` | `app/app_factory.py` (при создании приложения) | Нет | Низкий |
| **Catch‑all SPA‑маршрут (стр. 1548‑1562)** | Отдача `index.html` для всех非‑API путей | `Request`, `Path`, `FileResponse`, `HTTPException` | `app/core/routes.py` (или `app/static.py`) | Нет | Низкий |

---

### Списки объектов main.py

#### 1.Все HTTP routes  
| Метод | Путь | Краткое назначение |
|-------|------|--------------------|
| POST | `/api/webhook/telegram` | Прием обновлений от Telegram Bot |
| GET | `/api/health` | Health‑check |
| POST | `/api/export` | Экспорт в Obsidian |
| POST | `/api/auth/register` | Регистрация пользователя |
| GET | `/api/auth/verify-email` | Подтверждение email по токену |
| POST | `/api/auth/resend-verification` | Повторная отправка письма подтверждения |
| POST | `/api/auth/login` | Вход в систему |
| POST | `/api/auth/logout` | Выход (удаление сессии) |
| GET | `/api/auth/me` | Информация о текущем пользователе |
| GET | `/api/auth/status` | Статус аутентификации |
| POST | `/api/auth/initiate-password-reset` | Инициировать сброс пароля |
| POST | `/api/auth/reset-password` | Подтвердить сброс пароля токеном |
| POST | `/api/auth/initiate-email-change` | Инициировать смену email |
| POST | `/api/auth/confirm-email-change` | Подтвердить смену email токеном |
| GET | `/api/events` | SSE‑канал для событий |
| GET | `/api/now` | Текущее состояние NowBlock |
| GET | `/api/achievements` | Список достижений |
| GET | `/api/calendar/status` | Статус подключения к Google Calendar |
| GET | `/api/obsidian/status` | Статус настройки Obsidian |
| GET | `/api/obsidian/path` | Получить сохранённый путь к Obsidian |
| POST | `/api/obsidian/path` | Сохранить путь к Obsidian |
| GET | `/api/mais/groups` | Список MAIS‑групп |
| POST | `/api/mais/import` | Импорт расписания для группы |
| POST | `/api/mais/group` | Установить MAIS‑группу для пользователя |
| GET | `/api/google/calendars` | Список календарей пользователя |
| POST | `/api/onboarding/complete` | Завершить онбординг (группа + календарь) |
| POST | `/api/google/calendar/select` | Выбрать календарь для синхронизации |
| GET | `/api/google/auth` | Начало OAuth flow |
| GET | `/api/google/callback` | Callback от Google OAuth |
| GET | `/api/google/status` | Проверка статуса подключения к Google |
| POST | `/api/google/disconnect` | Отключить/отозвать Google токен |
| POST | `/api/debug/echo` | Эхо‑отладка |
| GET | `/api/mais/import_get` | Тестовый эндпоинт (возвращает group_name) |
| POST | `/api/telegram/link` | Сгенерировать код привязки Telegram |
| GET | `/api/telegram/status` | Статус привязки Telegram |
| POST | `/api/telegram/unlink` | Отвязать Telegram‑аккаунт |
| GET | `/api/notifications` | Список уведомлений пользователя |
| POST | `/api/notifications/{notification_id}/read` | Пометить уведомление как прочитанное |
| POST | `/api/notifications/toggle` | Переключить флаг уведомлений включено/выключено |
| GET | `/{full_path:path}` | Catch‑all: отдача фронтенда (SPA) |

#### 2.Функции бизнес‑логики (внутренние helper‑функции и маршруты, содержащие логику, не относящиеся к Clean‑рутинному CRUD)  
- `get_obsidian_vault_path()` → чтение пути из файла/env  
- `save_obsidian_vault_path(path)` → запись пути в файл  
- `check_mais_schedule_for_user(user, session)` → проверка изменений расписания и создание уведомлений  
- `periodic_mais_check()` → циклический запуск проверки для всех пользователей  
- `start_background_tasks()` → запуск фоновой задачи при стартапе  
- Маршруты с тяжёлой логикой: `/api/export`, `/api/now`, `/api/mais/import`, `/api/onboarding/complete`, `/api/google/*`, `/api/telegram/link`, уведомления  

#### 3.Startup / shutdown действия  
- **Startup**: `@app.on_event("startup") async def start_background_tasks(): …` (запуск `periodic_mais_check`)  
- Shutdown: не определено.

#### 4.Background tasks  
- `periodic_mais_check()` – бесконечный цикл с `asyncio.sleep(3600)`  
- `check_mais_schedule_for_user(user, session)` – вызывается из periodic task  

#### 5.Глобальные объекты (на уровне модуля)  
- `logger` – объект `logging.Logger`  
- `app` – экземпляр `FastAPI`  
- `db` – singleton `Database()`  
- `settings` – singleton `Settings()`  
- `OBSIDIAN_CONFIG_PATH` – `Path("data/obsidian_config.json")`  
- `frontend_dir` – `Path(__file__).parent / "web"`  
- `GOOGLE_OAUTH_AVAILABLE` – флаг доступности Google‑OAuth  
- `GoogleCalendarSyncService` – класс или `None`  
- `get_google_calendar_service` – функция или `None`  
- `SCOPES` (из импорта Google‑OAuth) – попадает в глобальную область только при успешном импорте  
- `event_publisher` – импортировано из `app.event` (глобальный объект)  

#### 6.Helper‑функции (чистые утилиты, не привязанные к роутам напрямую)  
- `get_obsidian_vault_path()`  
- `save_obsidian_vault_path(path)`  
- (возможно) `_calculate_elapsed_seconds` – импортируется из `app.focus.routes`, но не определяется здесь  

#### 7.Legacy / duplicate routes  
- Duplicates не обнаружены (каждый путь уникален).  
- Замечание: маршрут `/api/mais/import_get` кажется тестовым и не используется в продакшене – можно рассматривать как устаревший/избыточный.  
- Комментарий о «DEVELOPMENT ONLY: RESET GAMIFICATION» – пустой блок, legacy‑заглушка.  

#### 8.Импорты, которые станут избыточными после удаления каждого блока  
*(указаны только те импорты, которые используются **исключительно** в данном блоке; если импорт используется и в других частях файла, он не отмечается)*  

| Блок | Импорты, которые можно удалить после вынесения блока |
|------|------------------------------------------------------|
| Настройка логгирования | `logging`, `httpx`, `httpcore`, `urllib3` (но `httpx` использовался дальше – оставить) &lt;br&gt;Фактически только `logging` можно локализовать; остальные нужны глобально. |
| CORS‑middleware | `from fastapi.middleware.cors import CORSMiddleware` |
| Монтирование статики | `from fastapi.staticfiles import StaticFiles` |
| Инициализация БД/настроек | `from app.database.db import Database`&lt;br&gt;`from app.config import Settings` |
| Webhook Telegram | `from fastapi import BackgroundTasks, Request`&lt;br&gt;(`telegram_bot_app` импортируется позже внизу файла) |
| Функции Obsidian‑пути | `from pathlib import Path`&lt;br&gt;`import json`&lt;br&gt;`import os` |
| Проверка frontend‑директории | `from pathlib import Path` |
| Маршрут /api/health | Нет специфичных импорт‑ов (только декоратор `@app.get`) |
| Маршрут /api/export | `from app.sync.service import SyncService`&lt;br&gt;`from app.common.schedule_filters import …` (уже в глобальных импортах) |
| Блок авторизации | `from app.auth.schemas import …`&lt;br&gt;`from app.auth.service import …` (многие из них уже глобально импортированы; специфичные: `secrets` (глобально), `email_service` (создаётся локально)) |
| Блок сброса пароля/email | Аналогично авторизации |
| Маршрут /api/events | `from fastapi import Request, Depends`&lt;br&gt;`from fastapi.responses import StreamingResponse`&lt;br&gt;`from app.event import event_publisher` |
| Маршрут /api/now | `from app.focus.service import FocusService`&lt;br&gt;`from app.common.time import msk_now_naive`&lt;br&gt;`from app.common.schedule_filters import get_schedule_exclusions, lesson_is_visible, normalize_schedule_category`&lt;br&gt;`from app.focus.routes import _calculate_elapsed_seconds` (уже глобально) |
| Маршрут /api/achievements | `from app.database.models import UserStats` |
| Маршрут /api/calendar/status | `import os`&lt;br&gt;`from app.google_calendar.auth import SCOPES, get_credentials_path, get_token_path, get_google_calendar_service`&lt;br&gt;(условно: `from google.oauth2.credentials import Credentials`&lt;br&gt;`from google.auth.transport.requests import Request`) |
| Маршруты Obsidian статуса/пути | Уже покрыты функциями Obsidian‑пути (см. выше). |
| Маршруты MAIS groups/import/set‑group | `from app.mais_parser import async_fetch_group_schedule, async_fetch_groups, fetch_group_schedule, fetch_groups, parse_mais_schedule`&lt;br&gt;`from app.sync.service import SyncService`&lt;br&gt;(опционально) `from app.google_calendar.service import GoogleCalendarSyncService` |
| Маршруты Google OAuth (весь блок) | Все импорты из `app.google_calendar.*` + `from google_auth_oauthlib.flow import Flow` + `from fastapi import Request, Depends, …`&lt;br&gt;+ `from fastapi.responses import RedirectResponse`&lt;br&gt;+ `import os` |
| Маршрут /api/debug/echo | `from fastapi import Request` |
| Маршрут /api/mais/import_get | Нет особ. импортов. |
| Маршруты Telegram link/status/unlink | `from app.telegram.service import create_telegram_link_code, unlink_telegram_account`&lt;br&gt;`from app.config import Settings` (уже глобально) |
| Маршруты уведомлений | `from app.database.models import Notification` |
| Функция `check_mais_schedule_for_user` | `from app.mais_parser import async_fetch_group_schedule, parse_mais_schedule`&lt;br&gt;`from app.sync.service import SyncService`&lt;br&gt;`from app.google_calendar.service import GoogleCalendarSyncService` (опционально)&lt;br&gt;`from app.database.models import Notification`&lt;br&gt;`import os` (для TELEGRAM_BOT_TOKEN)&lt;br&gt;`import httpx` |
| Периодическая фоновая задача | `import asyncio`&lt;br&gt;`from datetime import timezone, utc_now` |
| Старт фоновой задачи | `import asyncio` |
| Catch‑all SPA‑маршрут | `from fastapi import Request, HTTPException`&lt;br&gt;`from fastapi.responses = FileResponse`&lt;br&gt;`from pathlib import Path` |

---

### Поэтапный план миграции (с минимальным риском регрессии)

&gt; **Цель** – вынести логические блоки из `app/main.py` в соответствующие модули, оставив в `main.py` только: создание приложения, подключение роутеров, глобальные объекты и минимальную конфигурацию. Все изменения выполняются последовательно с запуском тестов после каждого шага (если тесты отсутствуют – выполнять ручную проверку ключевых эндпоинтов).

| Шап | Описание действий | Файлы, которые затронуты | Критерии завершения |
|-----|-------------------|--------------------------|----------------------|
| **0** | Запустить `graphify update .` (обновить граф AST) и убедиться, что текущий зеленый build проходит. | `app/main.py` (чтение) | Граф актуален, нет ошибок импорта. |
| **1** | Вынести настройку логгирования в `app/logging_config.py`. В `main.py` заменить блок 22‑33 на `from app.logging_config import configure_logging; configure_logging()`. | `app/logging_config.py` (создать), `app/main.py` (изменить) | После изменения приложение стартует, логи выводятся в прежнем формате. |
| **2** | Вынести чтение/запись Obsidian‑пути в `app/obsidian/utils.py` (или `app/obsidian/service.py`). В `main.py` заменить функции `get_obsidian_vault_path`/`save_obsidian_vault_path` на импот из этого модуля. | `app/obsidian/utils.py`, `app/main.py` | Функции работают (через эндпоинты `/api/obsidian/path*`). |
| **3** | Создать `app/core/routes.py` и перенести туда: &lt;br&gt;• `/api/health` &lt;br&gt;• `/api/events` &lt;br&gt;• `/api/debug/echo` &lt;br&gt;• catch‑all SPA‑маршрут &lt;br&gt;При необходимости оставить в `main.py` только подключение этого роутера (`app.include_router(core_router, prefix="")`). | `app/core/routes.py`, `app/main.py` | Все перечисленные эндпоинты доступны и работают как прежде. |
| **4** | Перенести маршруты Obsidian (`/api/obsidian/status`, `/api/obsidian/path*`) в новый роутер `app/obsidian/routes.py` и подключить его в `main.py` с префиксом `/api/obsidian`. Удалить соответствующие блоки из `main.py`. | `app/obsidian/routes.py`, `app/main.py` | Эндпоинты Obsidian отвечают. |
| **5** | Перенести маршруты MAIS (`/api/mais/groups`, `/api/mais/import`, `/api/mais/group`) в `app/mais/routes.py` и подключить с префиксом `/api/mais`. &lt;br&gt;Примечание: импорт `async_fetch_group_schedule` и т.д. следует оставить в этом файле. | `app/mais/routes.py`, `app/main.py` | Маршруты MAIS работают, импорт расписания выполняется. |
| **6** | Перенести всё, связанное с Google‑OAuth и календарями, в пакет `app/google_calendar`: &lt;br&gt;• `routes.py` (все эндпоинты `/api/google/*` и `/api/onboarding/complete`, `/api/google/calendar/select`) &lt;br&gt;• оставить `auth.py` и `service.py` как есть (или переместить логику из `main.py` туда). | `app/google_calendar/routes.py`, возможно `app/google_calendar/service.py`, `app/main.py` | Все Google‑маршруты работают, токен хранится/обновляется, статус корректный. |
| **7** **Перенести бизнес‑логику авторизации** (регистрация, верификация, логин, logout, info, status, сброс пароля, смена email) в `app/auth/routes.py` и подключить с префиксом `/api/auth`. При этом: &lt;br&gt;• оставить `app/auth/service.py` и `schemas.py` без изменений; &lt;br&gt;• импортировать нужные зависимости (email service, settings, db) внутрь роутера. | `app/auth/routes.py`, `app/main.py` | Все эндпоинты `/api/auth/*` отвечают, токены/сессии создаются корректно. |
| **8** **Перенести маршрут `/api/now`** в уже существующий `app/focus/routes.py` (соответственно удалить блок из `main.py`). Потребуется импортировать `FocusService` и вспомогательные функции оттуда. | `app/focus/routes.py` (добавить), `app/main.py` | Эндпоинт `/api/now` возвращает текущее состояние NowBlock. |
| **9** **Перенести достижения** (`/api/achievements`) в `app/stats/routes.py` (уже существует). | `app/stats/routes.py` (добавить), `app/main.py` | Эндпоинт работает и выдаёт список достижений. |
| **10** **Перенести фоновые задачи** в `app/sync/tasks.py` (или `app/mais/tasks.py`): &lt;br&gt;• `check_mais_schedule_for_user` &lt;br&gt;• `periodic_mais_check` &lt;br&gt;Из `main.py` оставить только вызов `asyncio.create_task(periodic_mais_check())` внутри startup‑хендлера (или перенести хендлер в `app/app_factory.py`). | `app/sync/tasks.py` (создать), `app/main.py` (удалить определения функций, оставить только импорт и вызов) | Фоновая задача запускается при старте и периодически проверяет расписание; уведомления создаются корректно. |
| **11** **Очистка**: удалить закомментированный/dev‑only блок «RESET GAMIFICATION», тестовый эндпоинт `/api/mais/import_get`, неиспользуемые импорты (которые стали не нужны после выноса блоков). | `app/main.py` | Файл стал значительно короче, остались только: &lt;br&gt;• импорты глобальных объектов (db, settings, logger) &lt;br&gt;• создание приложения и подключение middleware &lt;br&gt;• подключение всех роутеров (auth, focus, schedule, gamification, stats, obsidian, mai, google_calendar, telegram, core, notifications) &lt;br&gt;• startup‑хендлер (вызов фоновой задачи) &lt;br&gt;• возможно небольшие функции-помощники, если они остались. |
| **12** Запустить полный набор тестов (если они есть) либо вручную проверить: &lt;br&gt;• health‑check, &lt;br&gt;• авторизационный flow (register → verify-email → login), &lt;br&gt;• экспорт в Obsidian, &lt;br&gt;• получение расписания Now, &lt;br&gt;• работу фоновой задачи (можно вызвать вручную через API или подождать tick), &lt;br&gt;• все остальные эндпоинты (telegram, notifications, google …). | – | Все функции работают как до рефакторинга; регрессии не обнаружены. |

**Общие рекомендации по снижению риска**

- Перед каждым выносом покрыть соответствующий набор эндпоинтов локальными тестами (или post‑collection вручную) – это даст быстро откат, если что‑то сломается.
- Делать коммиты после каждого шага, чтобы можно было вернуться при необходимости.
- При выносе роутеров сохранять точно такие же префиксы (`/api/*`) и обрабатывать `Depends` так же (внутри роутера импортировать `get_current_active_user` из `app.auth.service`).
- Для функций, использующих глобальные объекты (`db`, `settings`), передавать их явно через параметры роутера (например, `router = APIRouter(); @router.get(...) def foo(db: Session = Depends(get_db))`) – тогда роутер остаётся тестируемым без привязки к singleton.
- После выноса всех блоков проверить, что в `app/main.py` больше нет прямой бизнес‑логики (только конфигурация и подключение).

Следуя этому плану, основной файл `app/main.py` станет «тонким» конфигурационным хабом, а вся логика будет размещена в тематических модулях, что улучшит поддерживаемость и упростит дальнейшее рефакторинго‑развитие.