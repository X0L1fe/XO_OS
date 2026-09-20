# Graph Report - MAISync  (2026-09-19)

## Corpus Check
- 98 files · ~130,124 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1047 nodes · 2603 edges · 69 communities (59 shown, 10 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 195 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f0b0e28a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- zd
- main.1e7adafe.js
- s
- src_OLD/App.js
- src/App.js
- parse_ics
- telegram/service.py
- main.py
- n
- enterface.md
- ss
- auth/service.py
- get_token_path
- dependencies
- ms
- mais_parser.py
- ObsidianPath
- Changes Made for MAIS Schedule Parser Layer
- LessonData
- l
- Выполненные изменения бэкенда
- package.json
- i
- devDependencies
- development
- web/manifest.json
- User Guide
- public/manifest.json
- telegram_link
- EmailService
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
- post
- forEach
- Learn More
- nu
- Da
- Решение проблемы дублирования в Telegram боте
- sc
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
4. `User` - 47 edges
5. `ss()` - 44 edges
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
- `get_calendar_service()` --calls--> `get_credentials_path()`  [EXTRACTED]
  DEL_DATA.py → app/google_calendar/auth.py
- `get_calendar_service()` --calls--> `get_token_path()`  [EXTRACTED]
  DEL_DATA.py → app/google_calendar/auth.py
- `EmailService` --uses--> `Settings`  [INFERRED]
  app/email/service.py → app/config.py

## Import Cycles
- None detected.

## Communities (69 total, 10 thin omitted)

### Community 0 - "zd"
Cohesion: 0.06
Nodes (51): af(), bt(), constructor(), Cr(), ct(), dt(), ef(), fd() (+43 more)

### Community 1 - "main.1e7adafe.js"
Cohesion: 0.05
Nodes (44): Aa(), ai(), An(), as(), bf(), Br(), componentDidCatch(), df() (+36 more)

### Community 2 - "s"
Cohesion: 0.12
Nodes (51): ad(), ar(), b(), c(), d(), _e(), et(), fr() (+43 more)

### Community 3 - "src_OLD/App.js"
Cohesion: 0.07
Nodes (20): App(), Achievements(), CalendarObsidianBlock(), Header(), Login(), NowBlock(), Onboarding(), PlayerCard() (+12 more)

### Community 4 - "src/App.js"
Cohesion: 0.07
Nodes (20): App(), Achievements(), CalendarObsidianBlock(), Header(), Login(), NowBlock(), Onboarding(), PlayerCard() (+12 more)

### Community 5 - "parse_ics"
Cohesion: 0.11
Nodes (28): _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), Any, datetime (+20 more)

### Community 6 - "telegram/service.py"
Cohesion: 0.12
Nodes (29): TelegramLinkCode, error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files). (+21 more)

### Community 7 - "main.py"
Cohesion: 0.07
Nodes (51): get_user_from_session(), Settings, User, export_to_obsidian(), get_achievements(), get_calendar_status(), get_current_active_user(), get_current_user() (+43 more)

### Community 8 - "n"
Cohesion: 0.11
Nodes (35): ac(), At(), cc(), ce(), dc(), Dr(), ec(), fc() (+27 more)

### Community 9 - "enterface.md"
Cohesion: 0.06
Nodes (32): 10. Расписание, 11. Следующее событие, 12. Главный статистический блок, 13. Динамика нагрузки, 14. Top Subjects, 15. План против факта, 16. Достижения, 17. Streak (+24 more)

### Community 10 - "ss"
Cohesion: 0.13
Nodes (34): ao(), Bi(), ca(), ci(), di(), es(), Fe(), fi() (+26 more)

### Community 11 - "auth/service.py"
Cohesion: 0.15
Nodes (25): authenticate_user(), confirm_email_change(), create_session(), create_user(), delete_session(), get_password_hash(), initiate_email_change(), initiate_password_reset() (+17 more)

### Community 12 - "get_token_path"
Cohesion: 0.14
Nodes (20): get_credentials_path(), get_data_dir(), get_google_calendar_service(), get_token_path(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., Returns the path to the Google OAuth2 token file., Authenticates with Google Calendar API and returns a service object. Handles… (+12 more)

### Community 13 - "dependencies"
Cohesion: 0.10
Nodes (21): axios, react, react-dom, react-icons, react-router-dom, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+13 more)

### Community 14 - "ms"
Cohesion: 0.10
Nodes (30): ae(), ba(), cd(), cs(), dd(), ds(), ee(), gc() (+22 more)

### Community 15 - "mais_parser.py"
Cohesion: 0.09
Nodes (24): check_mais_schedule_for_user(), get_mais_groups(), import_mais_schedule(), periodic_mais_check(), Check for schedule changes for a specific user and create notifications if…, Background task that periodically checks for MAIS schedule changes for all…, Get list of MAIS groups., Import schedule for a given MAIS group name. (+16 more)

### Community 16 - "ObsidianPath"
Cohesion: 0.18
Nodes (16): AuthStatusResponse, Config, BaseModel, TokenResponse, UserBase, UserCreate, UserLogin, UserResponse (+8 more)

### Community 17 - "Changes Made for MAIS Schedule Parser Layer"
Cohesion: 0.13
Nodes (14): 1. Google Calendar Service Formatting (`app/google_calendar/service.py`), 2. Database Model Extensions (`app/database/models.py`), 3. Background Task for Periodic Checking (`app/main.py`), 4. API Endpoints (`app/main.py`), 5. MAIS Parser Enhancements (`app/mais_parser.py`), 6. Imports and Dependencies (`app/main.py`), Changes Made for MAIS Schedule Parser Layer, How It Works (+6 more)

### Community 18 - "LessonData"
Cohesion: 0.05
Nodes (69): build_parser(), cmd_export(), cmd_import_ics(), cmd_stats(), cmd_status(), main(), Export lessons to Obsidian., Show user statistics. (+61 more)

### Community 19 - "l"
Cohesion: 0.15
Nodes (25): A(), bd(), bo(), co(), Do(), ei(), er(), go() (+17 more)

### Community 20 - "Выполненные изменения бэкенда"
Cohesion: 0.15
Nodes (12): 1. Исправлена ошибка сравнения дат (`can't compare offset-naive and offset-aware datetimes`), 2. Изменён метод эндпоинта подтверждения email на GET с параметром в query string, 3. Устранена причина 500‑ошибки при регистрации, 4. Переименован импорт функции проверки email для избежания конфликта имён, 5. Обновлён граф знаний, Header.js, Sidebar.js, Выполненные изменения бэкенда (+4 more)

### Community 21 - "package.json"
Cohesion: 0.20
Nodes (9): author, description, keywords, license, main, name, private, proxy (+1 more)

### Community 22 - "i"
Cohesion: 0.19
Nodes (22): al(), bl(), Cl(), De(), dl(), el(), fl(), Gr() (+14 more)

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

### Community 29 - "EmailService"
Cohesion: 0.21
Nodes (7): EmailService, Отправьте электронное письмо для сброса пароля. Args: email: адрес электронной…, Сервис для отправки писем по SMTP., Отправьте электронное письмо с запросом подтверждения смены email. Args: email:…, Отправьте электронное письмо с подтверждением новой электронной почты. Args:…, Render a Jinja2 template with the given context. Args: template_name: Name of…, Отправьте электронное письмо с подтверждением регистрации. Args: email: адрес…

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

### Community 53 - "post"
Cohesion: 0.15
Nodes (17): complete_onboarding(), confirm_email_change_endpoint(), echo(), google_disconnect(), initiate_email_change_endpoint(), initiate_password_reset_endpoint(), Complete onboarding by saving group and calendar selection., Save the user's selected Google Calendar ID for synchronization. (+9 more)

### Community 54 - "forEach"
Cohesion: 0.18
Nodes (13): clear(), eject(), $f(), forEach(), hf(), If(), ks(), Qf() (+5 more)

### Community 55 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 56 - "nu"
Cohesion: 0.27
Nodes (13): au(), bs(), cu(), du(), eu(), fu(), nu(), ru() (+5 more)

### Community 58 - "Решение проблемы дублирования в Telegram боте"
Cohesion: 0.20
Nodes (9): Альтернативный подход (если subprocess нежелателен):, Анализ проблемы, Изменения в `app/telegram_bot.py`, Предлагаемое решение, Преимущества этого подхода:, Причина проблемы, Решение проблемы дублирования в Telegram боте, Следующие шаги: (+1 more)

### Community 59 - "sc"
Cohesion: 0.47
Nodes (6): bc(), Be(), kc(), sc(), wc(), xc()

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
- **174 isolated node(s):** `Config`, `short_name`, `name`, `icons`, `start_url` (+169 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `main.py` to `telegram/service.py`, `auth/service.py`, `get_token_path`, `mais_parser.py`, `ObsidianPath`, `LessonData`, `post`, `telegram_link`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `SyncService` connect `LessonData` to `mais_parser.py`, `main.py`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Why does `Database` connect `LessonData` to `ObsidianPath`, `main.py`, `telegram/service.py`, `mais_parser.py`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `l()` (e.g. with `b()` and `c()`) actually correct?**
  _`l()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `s()` (e.g. with `hd()` and `mf()`) actually correct?**
  _`s()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `n()` (e.g. with `ad()` and `ci()`) actually correct?**
  _`n()` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `User` (e.g. with `ObsidianPath` and `GoogleCalendarServiceProtocol`) actually correct?**
  _`User` has 4 INFERRED edges - model-reasoned connections that need verification._