## Roadmap MAISync / XO_OS

### Этап 0 — Baseline / фиксация текущего состояния

**Статус: завершён**

Цель — понять текущую архитектуру до рефакторинга.

* аудит `app/main.py`
* карта роутов
* карта зависимостей
* выявление циклических зависимостей
* выявление дублирующейся бизнес-логики
* определение целевых модулей
* фиксация frontend/backend контрактов
* сохранение рабочего baseline

---

# Phase 1 — Выделение инфраструктурных модулей

## 1A. Common / shared utilities

**Статус: завершён**

Выделено:

```text
app/common/
```

В частности:

```text
schedule_filters.py
```

В него вынесена единая логика:

* normalization
* category normalization
* subject exclusions
* category exclusions
* lesson visibility
* получение schedule exclusions

Принцип:

```text
business logic
      ↓
common
```

а не:

```text
schedule → main
focus → schedule
main → focus
```

---

# Phase 2 — Выделение существующих крупных доменов

## 2A. Stats

**Статус: завершён**

Выделено:

```text
app/stats/
├── __init__.py
├── routes.py
└── service.py
```

Ответственность:

```text
HTTP
 ↓
StatsService
 ↓
DB / common
```

Из `main.py` убрана статистическая бизнес-логика.

---

## 2B. Gamification

**Статус: базовое выделение завершено**

Выделено:

```text
app/gamification/
├── __init__.py
├── routes.py
└── service.py
```

Существующий API:

```text
GET  /api/gamification/
PUT  /api/gamification/settings
POST /api/gamification/dev/reset
```

Также используется canonical event:

```text
xo-os:gamification-updated
```

### Но это ещё не финальная gamification-архитектура.

Следующая стадия должна переработать саму механику:

```text
Focus Session
      ↓
Result verification
      ↓
XPTransaction
      ↓
Gamification
      ↓
frontend event
```

---

# Phase 3 — Schedule + Focus

## 3A. Schedule common logic

**Статус: завершён**

Вся schedule-filter логика консолидирована в:

```text
app/common/schedule_filters.py
```

Commit:

```text
1bba388
```

---

# 3B. Schedule Router Extraction

## 3B.1 — Route compatibility

**Статус: завершён**

Работают оба URL:

```text
GET /api/schedule
GET /api/schedule/
```

При этом OpenAPI показывает только canonical:

```text
/api/schedule
```

Проверено:

* unauthorized → `401`
* authorized → `200`
* filters → `200`
* OpenAPI
* dependency graph
* frontend compatibility

---

## 3B.2 — Focus → canonical Schedule filters

**Статус: завершён**

Focus больше не должен иметь собственную реализацию schedule-filter логики.

Архитектура:

```text
FocusService
      ↓
common.schedule_filters
      ↓
ScheduleExclusion
```

Проверено отсутствие:

* локальных `normalize_*`
* локальных `lesson_is_*`
* `focus → main`

---

## 3B.3 — Functional Schedule ↔ Focus integration

**Статус: завершён**

Это текущая контрольная точка.

Проверяется уже не только структура файлов, но и runtime-поведение:

```text
Schedule filters
        ↓
current lesson
        ↓
Focus
        ↓
visibility / exclusions
```

То есть после 3B.3 schedule filtering считается рабочей частью доменной логики Focus.

---

# Phase 4 — Focus Session как полноценный домен

**Следующий большой этап.**

Сейчас Focus уже вынесен структурно, но его бизнес-модель ещё нужно довести до целевой.

Целевая структура:

```text
app/focus/
├── __init__.py
├── routes.py
├── service.py
├── schemas.py
└── verification.py
```

При необходимости:

```text
app/focus/repository.py
```

Но repository не вводить автоматически — только если DB-доступ действительно начинает мешать сервисному слою.

---

## 4A. Focus lifecycle

Нормализовать жизненный цикл:

```text
START
  ↓
ACTIVE
  ↓
PAUSED
  ↓
ACTIVE
  ↓
COMPLETED
```

Также:

```text
CANCELLED
```

если это необходимо текущему UX.

API:

```text
POST /api/focus/start
POST /api/focus/{id}/pause
POST /api/focus/{id}/resume
POST /api/focus/{id}/complete
GET  /api/focus/active
GET  /api/focus/{id}
```

Главное правило:

> backend сам определяет текущий lesson.

Frontend не должен определять, какой урок можно начать.

---

# Phase 5 — Focus Evidence

Добавляется полноценная модель результата.

Существующий:

```text
FocusEvidence
```

доводится до единого контракта.

Типы:

```text
text
url
image
file
```

Поток:

```text
Focus Session
      ↓
goal
      ↓
evidence
      ↓
verification
```

Важно разделить:

```text
duration
```

и

```text
result
```

Продолжительность сама по себе не является доказательством результата.

---

# Phase 6 — Verification / Local AI

Это отдельный домен внутри Focus.

Целевая архитектура:

```text
app/ai/
├── __init__.py
├── service.py
├── client.py
└── verification.py
```

Но AI должен быть **инфраструктурой проверки**, а не самостоятельной бизнес-логикой Focus.

---

## 6A. AI provider

Используется существующий локальный стек:

```text
Qwen2.5-VL-7B-Instruct-Q4_K_M
        +
llama.cpp
        +
mmproj-f16.gguf
```

Endpoint:

```text
http://127.0.0.1:8080/v1
```

Python:

```text
OpenAI client
```

Не добавляем:

* новый AI server
* новый framework
* другой model runtime
* LangChain и т.п.

---

## 6B. Verification contract

AI проверяет:

```text
goal ↔ evidence
```

а не:

```text
"насколько умный пользователь"
"насколько хорошо он работал"
"сколько времени он сидел"
```

Статусы:

```text
not_required
pending
approved
partial
rejected
error
```

Confidence:

```text
diagnostic only
```

Confidence не должен напрямую определять XP.

---

# Phase 7 — Async verification

AI-проверка не должна блокировать completion.

Целевой поток:

```text
POST /focus/{id}/complete
          ↓
session completed
          ↓
evidence saved
          ↓
verification = pending
          ↓
HTTP response
          ↓
background verification
          ↓
approved / partial / rejected / error
```

То есть пользователь не должен ждать inference.

---

# Phase 8 — XP / Gamification redesign

Это важная часть всей архитектуры.

Сейчас gamification исторически завязана на sync/import.

Нужно перейти к:

```text
real activity
      ↓
Focus result
      ↓
XP transaction
```

---

## 8A. Manual completion

Пример целевой модели:

```text
manual completion ≈ 3 XP
```

---

## 8B. AI verified result

Базовая награда:

```text
≈ 10 XP
```

плюс возможный quality bonus.

При этом:

```text
XP ≠ duration
```

Нельзя сделать:

```text
2 часа = 20 XP
4 часа = 40 XP
```

---

# Phase 9 — Anti-farming

Критически важно сделать reward idempotent.

Для одной lesson occurrence:

```text
one main reward
```

Повторный:

```text
complete
complete
complete
```

не должен генерировать бесконечный XP.

Для этого `XPTransaction` становится audit ledger.

Целевая связь:

```text
XPTransaction
    ↓
source_type
source_id
```

Например:

```text
source_type = focus_completion
source_id = focus_session_id
```

Или отдельный lesson-occurrence ID, если он будет введён.

---

# Phase 10 — Real activity streak

Текущий исторический streak был связан с импортом/sync.

Это нужно заменить.

Целевая модель:

```text
qualifying activity
        ↓
streak
```

Например:

```text
completed focus
verified result
other explicitly qualifying activity
```

Но:

```text
MAIS sync
```

не должна автоматически считаться учебной активностью.

---

# Phase 11 — Gamification event architecture

Сделать единый поток событий:

```text
Focus
 ↓
XP transaction
 ↓
Gamification state
 ↓
event
```

Events:

```text
xo-os:focus-updated
xo-os:gamification-updated
xo-os:schedule-filters-changed
```

Frontend должен реагировать на события, а не самостоятельно вычислять backend state.

---

# Phase 12 — Auth extraction

После стабилизации Focus/Schedule/Gamification.

Целевая структура:

```text
app/auth/
├── __init__.py
├── routes.py
├── service.py
├── dependencies.py
└── schemas.py
```

Разделить:

```text
HTTP
 ↓
AuthService
 ↓
User / Session / verification
```

Из `main.py` убрать:

* register
* login
* email verification
* session handling
* auth-specific business logic

---

# Phase 13 — Email extraction

Цель:

```text
app/email/
├── __init__.py
├── service.py
├── templates/
└── ...
```

Auth не должен напрямую знать детали SMTP/email implementation.

Правильно:

```text
AuthService
   ↓
EmailService
```

а не:

```text
AuthService
   ↓
SMTP implementation
```

---

# Phase 14 — Telegram extraction

Уже существует:

```text
app/telegram/
```

Нужно полностью убрать Telegram business logic из `main.py`.

Целевая схема:

```text
app/telegram/
├── __init__.py
├── routes.py
├── service.py
└── handlers.py
```

Разделить:

```text
Telegram transport
```

и

```text
Telegram business logic
```

---

# Phase 15 — Sync extraction

Следующий крупный домен.

Цель:

```text
app/sync/
├── __init__.py
├── routes.py
├── service.py
└── ...
```

Сейчас sync тесно связан с:

```text
MAIS parser
DB
Google Calendar
gamification
background task
```

Нужно сделать:

```text
SyncService
    ↓
MAIS parser
    ↓
DB
    ↓
events
```

а не держать orchestration в `main.py`.

---

# Phase 16 — Google Calendar isolation

Google Calendar должен быть отдельным integration layer.

Целевая архитектура:

```text
app/google_calendar/
├── auth.py
├── service.py
└── ...
```

И уже есть большая часть этого.

Нужно убрать из `main.py` прямую orchestration-логику.

Цель:

```text
SyncService
      ↓
GoogleCalendarService
```

---

# Phase 17 — MAIS parser isolation

Сделать parser полностью независимым от FastAPI.

```text
app/mais_parser.py
```

должен заниматься:

```text
input
 ↓
parse
 ↓
normalized domain data
```

а не:

```text
parse
 ↓
HTTP
 ↓
DB
 ↓
XP
```

---

# Phase 18 — Background jobs

Сейчас в `main.py` находится periodic MAIS task.

Её нужно убрать из application bootstrap.

Целевая структура:

```text
app/jobs/
├── __init__.py
├── sync.py
└── ...
```

или аналогичный минимальный слой.

Поток:

```text
scheduler
   ↓
SyncService
```

а не:

```text
scheduler
   ↓
main.py
   ↓
500 lines of business logic
```

---

# Phase 19 — AI / other integrations

После Focus AI:

```text
app/ai/
```

должен стать независимым integration layer.

Другие внешние интеграции также не должны импортировать:

```text
app.main
```

Правило:

```text
main.py
```

только собирает приложение.

---

# Phase 20 — `main.py` final cleanup

Финальная цель:

```text
app/main.py
```

должен стать практически composition root.

Примерно:

```python
app = FastAPI(...)

app.add_middleware(...)
app.include_router(auth_router)
app.include_router(schedule_router)
app.include_router(focus_router)
app.include_router(stats_router)
app.include_router(gamification_router)
app.include_router(sync_router)
app.include_router(telegram_router)
...
```

Плюс:

* startup
* shutdown
* middleware
* static/frontend serving
* configuration

Но не domain business logic.

---

# Phase 21 — Domain dependency rules

После extraction нужно зафиксировать архитектурные ограничения.

Целевая схема:

```text
                ┌──────────────┐
                │    main      │
                └──────┬───────┘
                       │
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
     auth           schedule          focus
                       │                │
                       └──────┬─────────┘
                              ↓
                           common
```

Интеграции:

```text
focus ─────→ ai
sync  ─────→ MAIS
sync  ─────→ google_calendar
auth  ─────→ email
```

Но:

```text
domain → main
```

запрещено.

---

# Phase 22 — Database/domain cleanup

После стабилизации сервисов.

Проверить:

* модели
* relationships
* cascade
* unique constraints
* indexes
* nullable
* timestamps
* audit fields

Особенно:

```text
FocusSession
FocusEvidence
XPTransaction
ScheduleExclusion
User
UserStats
```

---

# Phase 23 — API contracts / schemas

Постепенно убрать передачу сырых ORM объектов через API.

Добавить:

```text
schemas.py
```

по доменам:

```text
auth
schedule
focus
gamification
stats
sync
```

Поток:

```text
ORM
 ↓
service
 ↓
Pydantic schema
 ↓
API
```

---

# Phase 24 — Frontend integration cleanup

После стабилизации backend API.

Проверить frontend:

```text
ScheduleList
NowBlock
NextEvent
PlayerCard
Stats
Achievements
Settings
Focus UI
```

Главные правила:

* frontend не вычисляет backend business state;
* frontend не дублирует schedule filtering;
* frontend получает state через API;
* события используются для синхронизации UI;
* canonical API URLs используются везде.

---

# Phase 25 — Tests

До этого тесты были в основном smoke/static.

Нужен нормальный integration layer.

## Schedule

```text
unauthorized
authorized
filters
exclude subject
exclude category
visibility
slash compatibility
```

## Focus

```text
start
pause
resume
complete
active
wrong lesson
excluded lesson
evidence
```

## Verification

```text
pending
approved
partial
rejected
error
```

## XP

```text
manual reward
AI reward
quality bonus
duplicate completion
duplicate verification
```

## Streak

```text
qualifying activity
non-qualifying activity
same-day activity
consecutive days
gap
```

---

# Phase 26 — Architecture validation

Финальный static audit:

```text
main imports
dependency graph
cycles
domain boundaries
duplicate helpers
direct DB access
router prefixes
API routes
```

Особенно проверить:

```text
grep / AST:
app.main imports
main → domain
domain → main
duplicate schedule logic
duplicate XP logic
```

---

# Phase 27 — Runtime regression suite

Полный smoke:

```text
Auth
 ↓
Schedule
 ↓
Focus
 ↓
Evidence
 ↓
AI verification
 ↓
XP
 ↓
Gamification
 ↓
Stats
 ↓
Frontend
```

Проверить одновременно:

* 401
* 403
* 404
* 422
* 500
* redirects
* trailing slash
* cookies
* Bearer/session auth
* CORS
* frontend fallback

---

# Phase 28 — Production cleanup

Удалить:

* временные scripts
* debug endpoints, которые больше не нужны
* старые compatibility helpers
* dead code
* дублирующиеся функции
* старые imports
* временные AI scripts
* graphify artifacts, если они не являются частью репозитория

Проверить:

```text
git status
```

и отдельно:

```text
graphify-out/
```

чтобы аудит архитектуры не загрязнял production diff.

---

# Phase 29 — Documentation

Финально зафиксировать:

```text
ARCHITECTURE.md
API.md
FOCUS.md
GAMIFICATION.md
AI_VERIFICATION.md
```

Минимальная документация должна объяснять:

```text
как определяется current lesson
как работают exclusions
как создаётся FocusSession
как добавляется evidence
как работает verification
как начисляется XP
как предотвращается farming
как считается streak
```

---

# Итоговая последовательность

С учётом текущего состояния:

```text
0   Baseline                         DONE
1A  Common                           DONE
2A  Stats                            DONE
2B  Gamification extraction          DONE
3A  Schedule common                  DONE
3B.1 Schedule routes                 DONE
3B.2 Focus integration               DONE
3B.3 Functional integration          DONE
────────────────────────────────────────────
4   Focus domain finalization        NEXT
5   Evidence
6   AI verification
7   Async verification
8   XP redesign
9   Anti-farming
10  Real activity streak
11  Gamification events
12  Auth extraction
13  Email extraction
14  Telegram extraction
15  Sync extraction
16  Google Calendar isolation
17  MAIS parser isolation
18  Background jobs
19  AI/integrations cleanup
20  main.py final cleanup
21  Dependency rules
22  DB/domain cleanup
23  API schemas
24  Frontend cleanup
25  Tests
26  Architecture audit
27  Runtime regression
28  Production cleanup
29  Documentation
```

### Главная архитектурная цель

В конечном состоянии:

```text
                         ┌──────────────┐
                         │   FastAPI    │
                         │   main.py    │
                         └──────┬───────┘
                                │
              ┌─────────────────┼─────────────────┐
              ↓                 ↓                 ↓
            Auth             Schedule           Focus
              │                 │                 │
            Email             Common              AI
                                │                  │
                                └───────┬──────────┘
                                        ↓
                                   Gamification
                                        │
                                        ↓
                                      Stats


Integrations:
    Sync ──→ MAIS
    Sync ──→ Google Calendar
    Telegram ──→ domain services
    Jobs ──→ SyncService
```