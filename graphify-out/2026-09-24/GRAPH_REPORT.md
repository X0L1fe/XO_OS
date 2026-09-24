# Graph Report - .  (2026-09-21)

## Corpus Check
- 67 files · ~129,087 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1055 nodes · 2496 edges · 94 communities (75 shown, 19 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 181 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Array/Collection Utilities
- React Component Lifecycle
- Frontend UI Components
- Core Application Services
- iCalendar Parsing
- Array/Collection Utilities (Set 2)
- UI Design Specifications
- Telegram Bot Integration
- Array/Collection Utilities (Set 3)
- Array/Collection Utilities (Set 4)
- Data Synchronization Service
- Authentication Service
- Application Navigation & Callbacks
- Array/Collection Utilities (Set 5)
- Lesson Data & Sync Diff
- Documentation
- Google Calendar Service
- Release Notes & Bot Solution
- Frontend Dependencies
- Configuration & Email Service
- Google Calendar Auth & Data Deletion
- Array/Collection Utilities (Set 6)
- Array/Collection Utilities (Set 7)
- Release Tracking
- Database Layer
- Web Application Documentation
- Command Line Interface
- Authentication API Endpoints
- AbortController Utilities
- Array/Collection Utilities (Set 8)
- Array/Collection Utilities (Set 9)
- Array/Collection Utilities (Set 10)
- Diff Algorithm & Testing
- Array/Collection Utilities (Set 11)
- Array/Collection Utilities (Set 12)
- Array/Collection Utilities (Set 13)
- Bot Solution Documentation
- Package Metadata
- Auth Schemas (Pydantic Models)
- Frontend Fixes Documentation
- Build Tools (PostCSS)
- PWA Manifest
- Fixes Summary
- Project Summary
- Web PWA Manifest
- Array/Collection Utilities (Set 14)
- Debug Information
- Array/Collection Utilities (Set 15)
- Logout & User Info
- Telegram API Schemas
- Fix Summary
- NPM Scripts
- Periodic MAIS Check
- React/Jest Configuration
- Documentation Files
- Testing Library React
- QuoteNote Component
- Database Initialization
- Sync Initialization
- Telegram Initialization
- Enterface Design Document
- Fix Summary Markdown
- Fixes Summary Markdown
- Logo Asset
- Memory File
- Notes File
- Package Reference
- Status Checking
- Tailwind CSS Framework
- Test Initialization
- Todo File
- Craco Build Config
- Postcss Build Config
- Web HTML Entry Point

## God Nodes (most connected - your core abstractions)
1. `l()` - 80 edges
2. `s()` - 56 edges
3. `n()` - 50 edges
4. `ss()` - 48 edges
5. `User` - 47 edges
6. `i()` - 42 edges
7. `hl()` - 29 edges
8. `rd()` - 29 edges
9. `_t()` - 24 edges
10. `ms()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `make_new()` --calls--> `LessonData`  [EXTRACTED]
  tests/test_diff.py → app/ics/parser.py
- `test_create_update_and_delete()` --calls--> `SyncService`  [EXTRACTED]
  tests/test_sync.py → app/sync/service.py
- `test_lab_multiple_teachers()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `test_lecture_parsing()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `CHANGES_SUMMARY` --conceptually_related_to--> `FIX_LOG`  [INFERRED]
  CHANGES_SUMMARY.md → FIX_LOG.txt

## Import Cycles
- None detected.

## Communities (94 total, 19 thin omitted)

### Community 0 - "Array/Collection Utilities"
Cohesion: 0.06
Nodes (50): af(), br(), bt(), cf(), constructor(), Cr(), ct(), df() (+42 more)

### Community 1 - "React Component Lifecycle"
Cohesion: 0.06
Nodes (38): ad(), An(), as(), Dn(), ef(), ei(), fr(), ic() (+30 more)

### Community 2 - "Frontend UI Components"
Cohesion: 0.05
Nodes (23): App(), Achievements(), CalendarObsidianBlock(), Header(), Login(), NextEvent(), NowBlock(), Onboarding() (+15 more)

### Community 3 - "Core Application Services"
Cohesion: 0.07
Nodes (49): get_user_from_session(), User, auth_status(), export_to_obsidian(), get_achievements(), get_calendar_status(), get_current_active_user(), get_current_user() (+41 more)

### Community 4 - "iCalendar Parsing"
Cohesion: 0.07
Nodes (40): _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), Any, datetime (+32 more)

### Community 5 - "Array/Collection Utilities (Set 2)"
Cohesion: 0.16
Nodes (39): A(), ao(), b(), C(), co(), d(), _e(), et() (+31 more)

### Community 6 - "UI Design Specifications"
Cohesion: 0.06
Nodes (32): 10. Расписание, 11. Следующее событие, 12. Главный статистический блок, 13. Динамика нагрузки, 14. Top Subjects, 15. План против факта, 16. Достижения, 17. Streak (+24 more)

### Community 7 - "Telegram Bot Integration"
Cohesion: 0.12
Nodes (29): TelegramLinkCode, error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files). (+21 more)

### Community 8 - "Array/Collection Utilities (Set 3)"
Cohesion: 0.13
Nodes (31): al(), Bl(), bo(), Cl(), eo(), er(), fo(), go() (+23 more)

### Community 9 - "Array/Collection Utilities (Set 4)"
Cohesion: 0.11
Nodes (30): ar(), ba(), Bd(), bf(), De(), Dr(), es(), fd() (+22 more)

### Community 10 - "Data Synchronization Service"
Cohesion: 0.13
Nodes (18): UserStats, _apply_lesson_data(), _create_lesson(), GoogleCalendarServiceProtocol, Database, datetime, DiffResult, LessonData (+10 more)

### Community 11 - "Authentication Service"
Cohesion: 0.15
Nodes (25): authenticate_user(), confirm_email_change(), create_session(), create_user(), delete_session(), get_password_hash(), initiate_email_change(), initiate_password_reset() (+17 more)

### Community 12 - "Application Navigation & Callbacks"
Cohesion: 0.08
Nodes (26): complete_onboarding(), echo(), google_callback(), google_disconnect(), mark_notification_as_read(), Complete onboarding by saving group and calendar selection., Save the user's selected Google Calendar ID for synchronization., Handle Google OAuth2 callback. (+18 more)

### Community 13 - "Array/Collection Utilities (Set 5)"
Cohesion: 0.13
Nodes (26): Bi(), di(), El(), Ga(), ia(), Ir(), is(), ji() (+18 more)

### Community 14 - "Lesson Data & Sync Diff"
Cohesion: 0.15
Nodes (18): LessonData, Нормализованное занятие MAISync. source_uid: Оригинальный UID из ICS. Сохраняем…, Совместимость с предыдущей версией проекта. В будущем лучше везде перейти на…, Хэш всех изменяемых данных занятия. Если хэш поменялся — занятие необходимо…, _as_local(), _date_distance_days(), DiffResult, _find_best_match() (+10 more)

### Community 15 - "Documentation"
Cohesion: 0.09
Nodes (21): API Description, Architecture Overview, CLI Commands, Conflict Resolution, Dependencies, Environment Variables, License, Main Components (+13 more)

### Community 16 - "Google Calendar Service"
Cohesion: 0.13
Nodes (16): Lesson, _event_to_lesson_key(), GoogleCalendarSyncService, _lesson_to_google_event(), Database, datetime, DiffResult, LessonData (+8 more)

### Community 17 - "Release Notes & Bot Solution"
Cohesion: 0.10
Nodes (21): bot_solution, SOLUTION_SUMMARY, 1. Исправлена ошибка сравнения дат (`can't compare offset-naive and offset-aware datetimes`), 2. Изменён метод эндпоинта подтверждения email на GET с параметром в query string, 3. Устранена причина 500‑ошибки при регистрации, 4. Переименован импорт функции проверки email для избежания конфликта имён, 5. Обновлён граф знаний, Header.js (+13 more)

### Community 18 - "Frontend Dependencies"
Cohesion: 0.11
Nodes (20): axios, react, react-dom, react-icons, react-router-dom, react-scripts, @testing-library/dom, @testing-library/user-event (+12 more)

### Community 19 - "Configuration & Email Service"
Cohesion: 0.16
Nodes (10): Settings, EmailService, Отправьте электронное письмо для сброса пароля. Args: email: адрес электронной…, Сервис для отправки писем по SMTP., Отправьте электронное письмо с запросом подтверждения смены email. Args: email:…, Отправьте электронное письмо с подтверждением новой электронной почты. Args:…, Render a Jinja2 template with the given context. Args: template_name: Name of…, Отправьте электронное письмо с подтверждением регистрации. Args: email: адрес… (+2 more)

### Community 20 - "Google Calendar Auth & Data Deletion"
Cohesion: 0.15
Nodes (16): get_credentials_path(), get_data_dir(), get_google_calendar_service(), get_token_path(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., Returns the path to the Google OAuth2 token file., Authenticates with Google Calendar API and returns a service object. Handles… (+8 more)

### Community 21 - "Array/Collection Utilities (Set 6)"
Cohesion: 0.21
Nodes (18): au(), Be(), cu(), du(), fu(), Gc(), gu(), hu() (+10 more)

### Community 22 - "Array/Collection Utilities (Set 7)"
Cohesion: 0.18
Nodes (17): ai(), ci(), componentDidCatch(), Fe(), fi(), gi(), gl(), hi() (+9 more)

### Community 23 - "Release Tracking"
Cohesion: 0.12
Nodes (17): CHANGES_SUMMARY, 1. Google Calendar Service Formatting (`app/google_calendar/service.py`), 2. Database Model Extensions (`app/database/models.py`), 3. Background Task for Periodic Checking (`app/main.py`), 4. API Endpoints (`app/main.py`), 5. MAIS Parser Enhancements (`app/mais_parser.py`), 6. Imports and Dependencies (`app/main.py`), Changes Made for MAIS Schedule Parser Layer (+9 more)

### Community 24 - "Database Layer"
Cohesion: 0.23
Nodes (9): Database, Base, Notification, Session, check_mais_schedule_for_user(), Check for schedule changes for a specific user and create notifications if…, DeclarativeBase, Path (+1 more)

### Community 25 - "Web Application Documentation"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 26 - "Command Line Interface"
Cohesion: 0.27
Nodes (12): build_parser(), cmd_export(), cmd_import_ics(), cmd_stats(), cmd_status(), main(), Database, Export lessons to Obsidian. (+4 more)

### Community 27 - "Authentication API Endpoints"
Cohesion: 0.15
Nodes (13): confirm_email_change_endpoint(), initiate_email_change_endpoint(), initiate_password_reset_endpoint(), UserCreate, Verify email using token from verification link., Resend verification email to user., Initiate password reset process., Initiate email change process (requires current authentication). (+5 more)

### Community 28 - "AbortController Utilities"
Cohesion: 0.25
Nodes (3): Aa(), Fa(), oi()

### Community 29 - "Array/Collection Utilities (Set 8)"
Cohesion: 0.25
Nodes (11): ae(), bs(), ca(), ee(), G(), gs(), J(), Ki() (+3 more)

### Community 30 - "Array/Collection Utilities (Set 9)"
Cohesion: 0.29
Nodes (9): bu(), ku(), lr(), nr(), or(), rr(), vu(), xu() (+1 more)

### Community 31 - "Array/Collection Utilities (Set 10)"
Cohesion: 0.20
Nodes (11): cs(), dd(), Hr(), hs(), ka(), ms(), od(), ps() (+3 more)

### Community 32 - "Diff Algorithm & Testing"
Cohesion: 0.53
Nodes (9): calculate_diff(), Сравнивает старое состояние с новым. Алгоритм: 1. Exact match по identity_key.…, make_new(), make_old(), test_date_change_is_moved(), test_exact_identity_is_updated(), test_new_lesson_is_created(), test_time_change_is_moved() (+1 more)

### Community 33 - "Array/Collection Utilities (Set 11)"
Cohesion: 0.33
Nodes (10): ac(), ec(), fs(), ks(), nc(), rc(), tc(), vs() (+2 more)

### Community 34 - "Array/Collection Utilities (Set 12)"
Cohesion: 0.29
Nodes (10): cc(), dc(), ds(), fc(), lu(), of(), sc(), uc() (+2 more)

### Community 35 - "Array/Collection Utilities (Set 13)"
Cohesion: 0.22
Nodes (10): dl(), fl(), hl(), ll(), qr(), Ur(), Vr(), Wr() (+2 more)

### Community 36 - "Bot Solution Documentation"
Cohesion: 0.20
Nodes (9): Альтернативный подход (если subprocess нежелателен):, Анализ проблемы, Изменения в `app/telegram_bot.py`, Предлагаемое решение, Преимущества этого подхода:, Причина проблемы, Решение проблемы дублирования в Telegram боте, Следующие шаги: (+1 more)

### Community 37 - "Package Metadata"
Cohesion: 0.20
Nodes (9): author, description, keywords, license, main, name, private, proxy (+1 more)

### Community 38 - "Auth Schemas (Pydantic Models)"
Cohesion: 0.36
Nodes (8): AuthStatusResponse, Config, BaseModel, TokenResponse, UserBase, UserCreate, UserLogin, UserResponse

### Community 39 - "Frontend Fixes Documentation"
Cohesion: 0.22
Nodes (8): FRONTEND_FIXES, Changes Made, Frontend Fixes for XO_OS, Header.js (`xo-os-web/src/components/Header.js`), How It Works, Notes, Sidebar.js (`xo-os-web/src/components/Sidebar.js`), README

### Community 40 - "Build Tools (PostCSS)"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 41 - "PWA Manifest"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 42 - "Fixes Summary"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 43 - "Project Summary"
Cohesion: 0.25
Nodes (7): 1. Email Verification Endpoint, 2. Registration Endpoint, 3. Import Alias, 4. Graph Update, Expected Results, Fixes Applied, Prerequisites

### Community 44 - "Web PWA Manifest"
Cohesion: 0.25
Nodes (8): SUMMARY, Changes Made, Current State, Google Calendar Setup, Installation, Running, Usage, XO_OS - Google Calendar Integration Summary

### Community 45 - "Array/Collection Utilities (Set 14)"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 46 - "Debug Information"
Cohesion: 0.29
Nodes (7): clear(), gr(), ju(), nd(), td(), Yr(), Zu()

### Community 47 - "Array/Collection Utilities (Set 15)"
Cohesion: 0.29
Nodes (6): Анализ дублирования событий в Google Calendar, Как проверить, какой случай у вас есть:, Почему вы всё ещё видите дублирование:, Следующие шаги:, Что можно сделать:, Что я проверил и исправил:

### Community 48 - "Logout & User Info"
Cohesion: 0.33
Nodes (6): At(), eu(), Jc(), md(), su(), wu()

### Community 49 - "Telegram API Schemas"
Cohesion: 0.40
Nodes (5): Any, get_current_user_info(), logout(), Log out the current user., Get the current user.

### Community 50 - "Fix Summary"
Cohesion: 0.60
Nodes (4): BaseModel, TelegramLinkResponse, TelegramStatusResponse, TelegramUnlinkResponse

### Community 51 - "NPM Scripts"
Cohesion: 0.40
Nodes (4): Дополнительные рекомендации для полной уверенности:, Изменения в файле `app/google_calendar/service.py`:, Исправлено дублирование событий в Google Calendar, Как это решает проблему дублирования:

### Community 52 - "Periodic MAIS Check"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 53 - "React/Jest Configuration"
Cohesion: 0.50
Nodes (4): periodic_mais_check(), Background task that periodically checks for MAIS schedule changes for all…, start_background_tasks(), on_event

### Community 54 - "Documentation Files"
Cohesion: 0.50
Nodes (4): react-app, react-app/jest, eslintConfig, extends

## Knowledge Gaps
- **180 isolated node(s):** `Config`, `1. Google Calendar Service Formatting (`app/google_calendar/service.py`)`, `3. Background Task for Periodic Checking (`app/main.py`)`, `5. MAIS Parser Enhancements (`app/mais_parser.py`)`, `6. Imports and Dependencies (`app/main.py`)` (+175 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Core Application Services` to `Telegram Bot Integration`, `Data Synchronization Service`, `Authentication Service`, `Application Navigation & Callbacks`, `Google Calendar Service`, `Telegram API Schemas`, `Configuration & Email Service`, `Database Layer`, `Command Line Interface`, `Authentication API Endpoints`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `SyncService` connect `Data Synchronization Service` to `Database Layer`, `Google Calendar Service`, `Command Line Interface`, `Core Application Services`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `Lesson` connect `Google Calendar Service` to `Diff Algorithm & Testing`, `Core Application Services`, `Data Synchronization Service`, `Lesson Data & Sync Diff`, `Configuration & Email Service`, `Database Layer`, `Command Line Interface`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `l()` (e.g. with `er()` and `hl()`) actually correct?**
  _`l()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `s()` (e.g. with `A()` and `bu()`) actually correct?**
  _`s()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `n()` (e.g. with `A()` and `ad()`) actually correct?**
  _`n()` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ss()` (e.g. with `i()` and `lo()`) actually correct?**
  _`ss()` has 2 INFERRED edges - model-reasoned connections that need verification._