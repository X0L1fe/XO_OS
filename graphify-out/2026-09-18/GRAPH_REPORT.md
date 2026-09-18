# Graph Report - MAISync  (2026-09-18)

## Corpus Check
- 75 files · ~119,870 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 989 nodes · 2505 edges · 64 communities (54 shown, 10 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 194 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `beb7f6fc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- forEach
- main.6f61398d.js
- s
- ms
- App.js
- LessonData
- telegram/service.py
- User
- rd
- enterface.md
- ss
- main.py
- get_google_calendar_service
- dependencies
- l
- mais_parser.py
- ObsidianPath
- Changes Made for MAIS Schedule Parser Layer
- Database
- nu
- Выполненные изменения бэкенда
- package.json
- Da
- devDependencies
- development
- web/manifest.json
- User Guide
- public/manifest.json
- telegram_link
- ._render_template
- Frontend Fixes for XO_OS
- scripts
- extends
- MAISync
- MAISync
- MAISync logo (XO in black rounded rectangle)
- MAISync
- STATUS
- TODO
- README
- WEB
- nr
- Learn More
- Решение проблемы дублирования в Telegram боте
- Usage
- Анализ дублирования событий в Google Calendar
- Telegram Bot for XO_OS
- Исправлено дублирование событий в Google Calendar
- xo_os
- Fixes Applied
- react-scripts

## God Nodes (most connected - your core abstractions)
1. `l()` - 74 edges
2. `s()` - 63 edges
3. `n()` - 49 edges
4. `ss()` - 44 edges
5. `User` - 43 edges
6. `i()` - 32 edges
7. `hl()` - 29 edges
8. `rd()` - 27 edges
9. `LessonData` - 25 edges
10. `Database` - 24 edges

## Surprising Connections (you probably didn't know these)
- `test_lab_multiple_teachers()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `test_lecture_parsing()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `ObsidianPath` --uses--> `Settings`  [INFERRED]
  app/main.py → app/config.py
- `ObsidianPath` --uses--> `Database`  [INFERRED]
  app/main.py → app/database/db.py
- `test_create_update_and_delete()` --calls--> `Database`  [EXTRACTED]
  tests/test_sync.py → app/database/db.py

## Import Cycles
- None detected.

## Communities (64 total, 10 thin omitted)

### Community 0 - "forEach"
Cohesion: 0.05
Nodes (58): af(), bt(), constructor(), Cr(), ct(), df(), dt(), eject() (+50 more)

### Community 1 - "main.6f61398d.js"
Cohesion: 0.05
Nodes (46): ai(), as(), bf(), Br(), cd(), componentDidCatch(), cs(), dd() (+38 more)

### Community 2 - "s"
Cohesion: 0.11
Nodes (43): al(), At(), bl(), Cl(), clear(), d(), De(), dl() (+35 more)

### Community 3 - "ms"
Cohesion: 0.10
Nodes (41): ac(), ae(), cc(), ce(), dc(), _e(), ee(), fc() (+33 more)

### Community 4 - "App.js"
Cohesion: 0.08
Nodes (19): App(), Achievements(), CalendarObsidianBlock(), Header(), Login(), NowBlock(), PlayerCard(), ScheduleList() (+11 more)

### Community 5 - "LessonData"
Cohesion: 0.07
Nodes (51): _build_identity_key(), _clean(), _detect_category(), LessonData, _parse_datetime(), _parse_description(), parse_ics(), Any (+43 more)

### Community 6 - "telegram/service.py"
Cohesion: 0.12
Nodes (29): TelegramLinkCode, error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files). (+21 more)

### Community 7 - "User"
Cohesion: 0.08
Nodes (35): User, export_to_obsidian(), get_achievements(), get_current_active_user(), get_current_user_info(), get_notifications(), get_now(), get_obsidian_path() (+27 more)

### Community 8 - "rd"
Cohesion: 0.12
Nodes (41): An(), ar(), b(), bc(), Be(), c(), ec(), et() (+33 more)

### Community 9 - "enterface.md"
Cohesion: 0.06
Nodes (32): 10. Расписание, 11. Следующее событие, 12. Главный статистический блок, 13. Динамика нагрузки, 14. Top Subjects, 15. План против факта, 16. Достижения, 17. Streak (+24 more)

### Community 10 - "ss"
Cohesion: 0.12
Nodes (40): ao(), ba(), Bi(), ca(), ci(), ef(), es(), Fe() (+32 more)

### Community 11 - "main.py"
Cohesion: 0.10
Nodes (47): authenticate_user(), confirm_email_change(), create_session(), create_user(), delete_session(), get_password_hash(), get_user_from_session(), initiate_email_change() (+39 more)

### Community 12 - "get_google_calendar_service"
Cohesion: 0.08
Nodes (26): get_credentials_path(), get_data_dir(), get_google_calendar_service(), get_token_path(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., Returns the path to the Google OAuth2 token file., Authenticates with Google Calendar API and returns a service object. Handles… (+18 more)

### Community 13 - "dependencies"
Cohesion: 0.10
Nodes (21): axios, react, react-dom, react-icons, react-router-dom, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+13 more)

### Community 14 - "l"
Cohesion: 0.10
Nodes (39): A(), ad(), bd(), bo(), co(), Do(), Dr(), ei() (+31 more)

### Community 15 - "mais_parser.py"
Cohesion: 0.08
Nodes (26): Notification, Session, check_mais_schedule_for_user(), get_mais_groups(), import_mais_schedule(), periodic_mais_check(), Check for schedule changes for a specific user and create notifications if…, Background task that periodically checks for MAIS schedule changes for all… (+18 more)

### Community 16 - "ObsidianPath"
Cohesion: 0.19
Nodes (15): AuthStatusResponse, Config, BaseModel, TokenResponse, UserBase, UserCreate, UserLogin, UserResponse (+7 more)

### Community 17 - "Changes Made for MAIS Schedule Parser Layer"
Cohesion: 0.13
Nodes (14): 1. Google Calendar Service Formatting (`app/google_calendar/service.py`), 2. Database Model Extensions (`app/database/models.py`), 3. Background Task for Periodic Checking (`app/main.py`), 4. API Endpoints (`app/main.py`), 5. MAIS Parser Enhancements (`app/mais_parser.py`), 6. Imports and Dependencies (`app/main.py`), Changes Made for MAIS Schedule Parser Layer, How It Works (+6 more)

### Community 18 - "Database"
Cohesion: 0.09
Nodes (38): build_parser(), cmd_export(), cmd_import_ics(), cmd_stats(), cmd_status(), main(), Export lessons to Obsidian., Show user statistics. (+30 more)

### Community 19 - "nu"
Cohesion: 0.27
Nodes (13): au(), bs(), cu(), du(), eu(), fu(), nu(), ru() (+5 more)

### Community 20 - "Выполненные изменения бэкенда"
Cohesion: 0.15
Nodes (12): 1. Исправлена ошибка сравнения дат (`can't compare offset-naive and offset-aware datetimes`), 2. Изменён метод эндпоинта подтверждения email на GET с параметром в query string, 3. Устранена причина 500‑ошибки при регистрации, 4. Переименован импорт функции проверки email для избежания конфликта имён, 5. Обновлён граф знаний, Header.js, Sidebar.js, Выполненные изменения бэкенда (+4 more)

### Community 21 - "package.json"
Cohesion: 0.20
Nodes (9): author, description, keywords, license, main, name, private, proxy (+1 more)

### Community 22 - "Da"
Cohesion: 0.23
Nodes (3): Aa(), Da(), oi()

### Community 23 - "devDependencies"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 24 - "development"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 25 - "web/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 26 - "User Guide"
Cohesion: 0.09
Nodes (21): API Description, Architecture Overview, CLI Commands, Conflict Resolution, Dependencies, Environment Variables, License, Main Components (+13 more)

### Community 27 - "public/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 28 - "telegram_link"
Cohesion: 0.22
Nodes (10): Создаёт одноразовый код привязки учетной записи Telegram и создаёт Telegram…, Return Telegram connection status., Unlink Telegram account., telegram_link(), telegram_status(), telegram_unlink(), BaseModel, TelegramLinkResponse (+2 more)

### Community 29 - "._render_template"
Cohesion: 0.20
Nodes (5): Отправьте электронное письмо для сброса пароля. Args: email: адрес электронной…, Отправьте электронное письмо с запросом подтверждения смены email. Args: email:…, Отправьте электронное письмо с подтверждением новой электронной почты. Args:…, Render a Jinja2 template with the given context. Args: template_name: Name of…, Отправьте электронное письмо с подтверждением регистрации. Args: email: адрес…

### Community 30 - "Frontend Fixes for XO_OS"
Cohesion: 0.29
Nodes (6): Changes Made, Frontend Fixes for XO_OS, Header.js (`xo-os-web/src/components/Header.js`), How It Works, Notes, Sidebar.js (`xo-os-web/src/components/Sidebar.js`)

### Community 31 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 32 - "extends"
Cohesion: 0.50
Nodes (4): react-app, react-app/jest, eslintConfig, extends

### Community 33 - "MAISync"
Cohesion: 0.67
Nodes (3): App, MAISync, Web

### Community 55 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 58 - "Решение проблемы дублирования в Telegram боте"
Cohesion: 0.20
Nodes (9): Альтернативный подход (если subprocess нежелателен):, Анализ проблемы, Изменения в `app/telegram_bot.py`, Предлагаемое решение, Преимущества этого подхода:, Причина проблемы, Решение проблемы дублирования в Telegram боте, Следующие шаги: (+1 more)

### Community 60 - "Usage"
Cohesion: 0.25
Nodes (7): Changes Made, Current State, Google Calendar Setup, Installation, Running, Usage, XO_OS - Google Calendar Integration Summary

### Community 61 - "Анализ дублирования событий в Google Calendar"
Cohesion: 0.29
Nodes (6): Анализ дублирования событий в Google Calendar, Как проверить, какой случай у вас есть:, Почему вы всё ещё видите дублирование:, Следующие шаги:, Что можно сделать:, Что я проверил и исправил:

### Community 62 - "Telegram Bot for XO_OS"
Cohesion: 0.29
Nodes (6): Direct URL fetch (optional), Forwarding from external bot, How it works, Setup, Telegram Bot for XO_OS, Usage

### Community 63 - "Исправлено дублирование событий в Google Calendar"
Cohesion: 0.40
Nodes (4): Дополнительные рекомендации для полной уверенности:, Изменения в файле `app/google_calendar/service.py`:, Исправлено дублирование событий в Google Calendar, Как это решает проблему дублирования:

### Community 69 - "Fixes Applied"
Cohesion: 0.25
Nodes (7): 1. Email Verification Endpoint, 2. Registration Endpoint, 3. Import Alias, 4. Graph Update, Expected Results, Fixes Applied, Prerequisites

## Knowledge Gaps
- **173 isolated node(s):** `Config`, `short_name`, `name`, `icons`, `start_url` (+168 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `telegram/service.py`, `main.py`, `mais_parser.py`, `ObsidianPath`, `Database`, `telegram_link`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `ObsidianPath`, `main.py`, `telegram/service.py`, `mais_parser.py`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Why does `parse_ics()` connect `LessonData` to `Database`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `l()` (e.g. with `b()` and `c()`) actually correct?**
  _`l()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `s()` (e.g. with `hd()` and `mf()`) actually correct?**
  _`s()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `n()` (e.g. with `ad()` and `ci()`) actually correct?**
  _`n()` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ss()` (e.g. with `i()` and `lo()`) actually correct?**
  _`ss()` has 2 INFERRED edges - model-reasoned connections that need verification._