# Graph Report - XO_OS  (2026-09-29)

## Corpus Check
- 116 files · ~115,946 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1520 nodes · 3744 edges · 120 communities (98 shown, 22 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 356 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f31e2157`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- l
- n
- App.js
- main.py
- parse_ics
- ii
- FocusService
- telegram/service.py
- Gc
- main.90559390.js
- sync/service.py
- EmailService
- post
- roadmap.md
- diff.py
- User Guide
- mais_parser.py
- User
- dependencies
- .session
- google_calendar/service.py
- StatsSection.js
- Phase 6 Audit Report
- test_focus_race_condition.py
- LessonData
- Learn More
- cli.py
- Settings.js
- yi
- EmailChangePage.jsx
- ScheduleList.js
- NowBlock.js
- calculate_diff
- DonutChart.js
- PasswordResetPage.jsx
- index.js
- Sidebar
- package.json
- auth/schemas.py
- web/index.html
- devDependencies
- development
- web/manifest.json
- react-scripts
- i
- public/manifest.json
- get_token_path
- nc
- Phase 8 Audit Report
- stats-router-extract.md
- Jr
- Database
- scripts
- Lesson
- extends
- MAISync
- _f
- dl
- Phase 5 Audit Report
- MAISync logo (XO in black rounded rectangle)
- documentation
- README
- Phase 5 Verification Report
- Текущая архитектура (монолит)
- Phase 7 Audit Report
- MAISync
- Phase 4 Audit Report
- Phase 9 Audit
- xo_os
- LlamaCppClient
- architecture-target.md
- focus.js
- service-boundaries.md
- bu
- LessonChange
- PHASE_8_STATUS.md
- create_test_lesson
- create_test_lesson
- RECOVERY AUDIT
- export_to_obsidian
- create_test_focus_session
- test_ai_verification_race_condition_postgres
- PHASE 3B.3.1 RESULT
- PHASE 3B.3.2 — REPOSITORY STATE
- PHASE 3B.3 RESULT
- PHASE_6_STATUS.md
- PHASE_7_STATUS.md
- create_session
- test_manual_completion_race_condition
- debug_manual_completion_race_condition
- Phase 25 — Tests
- Phase 2 — Выделение существующих крупных доменов
- 3B. Schedule Router Extraction
- Phase 6 — Verification / Local AI
- Phase 8 — XP / Gamification redesign
- Phase 1 — Выделение инфраструктурных модулей
- Phase 3 — Schedule + Focus
- Phase 4 — Focus Session как полноценный домен
- Roadmap MAISync / XO_OS
- Итоговая последовательность

## God Nodes (most connected - your core abstractions)
1. `User` - 100 edges
2. `l()` - 79 edges
3. `FocusService` - 69 edges
4. `Lesson` - 63 edges
5. `n()` - 59 edges
6. `o()` - 57 edges
7. `i()` - 57 edges
8. `Database` - 50 edges
9. `ii()` - 50 edges
10. `UserStats` - 33 edges

## Surprising Connections (you probably didn't know these)
- `TestFocusCompletion` --uses--> `VerificationResult`  [INFERRED]
  tests/test_focus_completion.py → app/ai/verification.py
- `TestFocusCompletionRaceCondition` --uses--> `VerificationResult`  [INFERRED]
  tests/test_focus_race_condition.py → app/ai/verification.py
- `TestFocusCompletion` --uses--> `AIVerificationService`  [INFERRED]
  tests/test_focus_completion.py → app/ai/verification.py
- `TestFocusCompletionRaceCondition` --uses--> `AIVerificationService`  [INFERRED]
  tests/test_focus_race_condition.py → app/ai/verification.py
- `TestFocusEvidence` --uses--> `Database`  [INFERRED]
  tests/test_focus_evidence.py → app/database/db.py

## Import Cycles
- None detected.

## Communities (120 total, 22 thin omitted)

### Community 0 - "l"
Cohesion: 0.12
Nodes (46): al(), An(), ao(), as(), At(), bs(), cs(), d() (+38 more)

### Community 1 - "n"
Cohesion: 0.10
Nodes (52): A(), ad(), ae(), b(), C(), Dn(), du(), _e() (+44 more)

### Community 2 - "App.js"
Cohesion: 0.13
Nodes (9): Achievements(), CalendarObsidianBlock(), Header(), Login(), NextEvent(), Onboarding(), PlayerCard(), RecentChanges() (+1 more)

### Community 3 - "main.py"
Cohesion: 0.08
Nodes (36): event_publisher(), events_endpoint(), get_calendar_status(), get_mais_groups(), get_notifications(), get_obsidian_path(), get_obsidian_status(), get_obsidian_vault_path() (+28 more)

### Community 4 - "parse_ics"
Cohesion: 0.11
Nodes (28): _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), Any, datetime (+20 more)

### Community 5 - "ii"
Cohesion: 0.10
Nodes (35): Aa(), bl(), Bo(), El(), Fa(), fl(), ia(), ii() (+27 more)

### Community 6 - "FocusService"
Cohesion: 0.04
Nodes (36): FocusService, Resume a paused focus session., Get the active focus session for the user, if any., Get a focus session by ID, ensuring it belongs to the user., Get all evidence for a focus session., Validate and prepare evidence for storage. Returns a tuple of (type, content,…, Start a new focus session for the user. The backend determines the current…, Add evidence to a focus session. (+28 more)

### Community 7 - "telegram/service.py"
Cohesion: 0.12
Nodes (29): TelegramLinkCode, error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files). (+21 more)

### Community 8 - "Gc"
Cohesion: 0.08
Nodes (47): au(), bf(), co(), cu(), De(), Dr(), ei(), eu() (+39 more)

### Community 9 - "main.90559390.js"
Cohesion: 0.04
Nodes (60): ai(), bd(), ca(), cf(), ci(), componentDidCatch(), da(), dd() (+52 more)

### Community 10 - "sync/service.py"
Cohesion: 0.18
Nodes (12): _apply_lesson_data(), _create_lesson(), datetime, # IMPORTANT:, Export all lessons to an Obsidian vault. Creates markdown files in…, Update user statistics and gamification data. Does NOT award XP for imported…, Import a list of LessonData objects (parsed from MAIS schedule or other…, Обновляет существующую БД-запись данными из ICS. (+4 more)

### Community 11 - "EmailService"
Cohesion: 0.10
Nodes (19): confirm_email_change(), Подтверждает смену email по токену и обновляет email пользователя. Также…, EmailService, Отправьте электронное письмо для сброса пароля. Args: email: адрес электронной…, Сервис для отправки писем по SMTP., Отправьте электронное письмо с запросом подтверждения смены email. Args: email:…, Отправьте электронное письмо с подтверждением новой электронной почты. Args:…, Render a Jinja2 template with the given context. Args: template_name: Name of… (+11 more)

### Community 12 - "post"
Cohesion: 0.11
Nodes (21): complete_onboarding(), echo(), google_disconnect(), mark_notification_as_read(), BackgroundTasks, post, Set the MAIS group for the current user., Complete onboarding by saving group and calendar selection. (+13 more)

### Community 13 - "roadmap.md"
Cohesion: 0.09
Nodes (22): Phase 10 — Real activity streak, Phase 11 — Gamification event architecture, Phase 12 — Auth extraction, Phase 13 — Email extraction, Phase 14 — Telegram extraction, Phase 15 — Sync extraction, Phase 16 — Google Calendar isolation, Phase 17 — MAIS parser isolation (+14 more)

### Community 14 - "diff.py"
Cohesion: 0.36
Nodes (10): _as_local(), _date_distance_days(), _find_best_match(), _lesson_score(), datetime, Оценивает вероятность того, что old и new — одно и то же занятие после…, Ищет лучшее fuzzy-сопоставление. Ограничиваем поиск 14 днями, чтобы не…, Приводит datetime к Europe/Moscow. SQLite может вернуть datetime без tzinfo… (+2 more)

### Community 15 - "User Guide"
Cohesion: 0.09
Nodes (21): API Description, Architecture Overview, CLI Commands, Conflict Resolution, Dependencies, Environment Variables, License, Main Components (+13 more)

### Community 16 - "mais_parser.py"
Cohesion: 0.11
Nodes (20): check_mais_schedule_for_user(), import_mais_schedule(), periodic_mais_check(), Check for schedule changes for a specific user and create notifications if…, Background task that periodically checks for MAIS schedule changes for all…, Import schedule for a given MAIS group name., start_background_tasks(), async_fetch_group_schedule() (+12 more)

### Community 17 - "User"
Cohesion: 0.07
Nodes (48): authenticate_user(), create_user(), get_current_active_user(), get_current_user(), get_password_hash(), get_user_from_session(), initiate_email_change(), initiate_password_reset() (+40 more)

### Community 18 - "dependencies"
Cohesion: 0.10
Nodes (21): axios, react, react-dom, react-icons, react-router-dom, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+13 more)

### Community 19 - ".session"
Cohesion: 0.08
Nodes (38): add_evidence_to_focus_session(), _calculate_elapsed_seconds(), get_active_focus_session(), get_focus_session(), pause_focus_session(), get, post, Calculate the elapsed seconds for a session, accounting for pauses. (+30 more)

### Community 20 - "google_calendar/service.py"
Cohesion: 0.17
Nodes (10): _event_to_lesson_key(), GoogleCalendarSyncService, _lesson_to_google_event(), datetime, Получает события из целевого календаря Google Calendar. Возвращает список…, Обнаруживает события в Google Calendar, у которых нет соответствующего…, Синхронизирует изменения (созданные, обновленные, удаленные, перемещенные) в…, Извлекает потенциальный идентификатор урока из события Google Calendar.… (+2 more)

### Community 21 - "StatsSection.js"
Cohesion: 0.17
Nodes (7): formatNumber(), PlanFact(), StatsSection(), formatNumber(), TopSubjects(), formatNumber(), WeeklyChart()

### Community 22 - "Phase 6 Audit Report"
Cohesion: 0.11
Nodes (18): A. Что проверено, B. Текущий AI architecture, C. AI request flow, D. AI response flow, E. VerificationResult contract, F. FocusSession verification lifecycle, G. FocusEvidence → AI integration, H. XP integration (+10 more)

### Community 23 - "test_focus_race_condition.py"
Cohesion: 0.09
Nodes (28): AIVerificationService, get_ai_verification_service(), Any, Verify the evidence against the goal using the AI model., Build a prompt for the AI to verify evidence against the goal. We ask for a…, Parse the response from the AI, expecting a JSON object. If the response is not…, VerificationResult, event_publisher() (+20 more)

### Community 24 - "LessonData"
Cohesion: 0.14
Nodes (18): LessonData, Нормализованное занятие MAISync. source_uid: Оригинальный UID из ICS. Сохраняем…, Совместимость с предыдущей версией проекта. В будущем лучше везде перейти на…, Хэш всех изменяемых данных занятия. Если хэш поменялся — занятие необходимо…, DiffResult, _apply_lesson_data(), _create_lesson(), GoogleCalendarServiceProtocol (+10 more)

### Community 25 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 26 - "cli.py"
Cohesion: 0.22
Nodes (12): build_parser(), cmd_export(), cmd_import_ics(), cmd_stats(), cmd_status(), main(), Export lessons to Obsidian., Show user statistics. (+4 more)

### Community 28 - "yi"
Cohesion: 0.60
Nodes (6): cc(), dc(), fc(), ic(), uc(), yi()

### Community 30 - "ScheduleList.js"
Cohesion: 0.40
Nodes (3): DEFAULT_CATEGORIES, getPluralForm(), ScheduleList()

### Community 31 - "NowBlock.js"
Cohesion: 0.60
Nodes (4): EMPTY_NOW, formatCurrentTime(), formatLessonType(), NowBlock()

### Community 32 - "calculate_diff"
Cohesion: 0.53
Nodes (9): calculate_diff(), Сравнивает старое состояние с новым. Алгоритм: 1. Exact match по identity_key.…, make_new(), make_old(), test_date_change_is_moved(), test_exact_identity_is_updated(), test_new_lesson_is_created(), test_time_change_is_moved() (+1 more)

### Community 33 - "DonutChart.js"
Cohesion: 0.50
Nodes (3): COLORS, DonutChart(), formatNumber()

### Community 37 - "package.json"
Cohesion: 0.20
Nodes (9): author, description, keywords, license, main, name, private, proxy (+1 more)

### Community 38 - "auth/schemas.py"
Cohesion: 0.24
Nodes (11): AuthStatusResponse, Config, BaseModel, TokenResponse, UserBase, UserCreate, UserLogin, UserResponse (+3 more)

### Community 40 - "devDependencies"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 41 - "development"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 42 - "web/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 44 - "i"
Cohesion: 0.12
Nodes (43): ba(), Bt(), Cr(), ct(), dt(), fd(), forEach(), Gd() (+35 more)

### Community 45 - "public/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 46 - "get_token_path"
Cohesion: 0.14
Nodes (20): get_credentials_path(), get_data_dir(), get_google_calendar_service(), get_token_path(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., Returns the path to the Google OAuth2 token file., Authenticates with Google Calendar API and returns a service object. Handles… (+12 more)

### Community 47 - "nc"
Cohesion: 0.33
Nodes (11): ac(), bi(), Cl(), ec(), fi(), ji(), nc(), rc() (+3 more)

### Community 48 - "Phase 8 Audit Report"
Cohesion: 0.12
Nodes (15): AI verified completion:, Current Focus Reward Flow, Current Gamification Events, Current Level Usage, Current Streak Usage, Current XP Formula, Current XP Sources, Current XPTransaction Usage (+7 more)

### Community 49 - "stats-router-extract.md"
Cohesion: 0.22
Nodes (7): Changes, Files Created, Files Modified, How to Apply, Summary, Verification, Why

### Community 50 - "Jr"
Cohesion: 0.08
Nodes (17): af(), clear(), constructor(), eject(), ha(), hf(), If(), Jr (+9 more)

### Community 51 - "Database"
Cohesion: 0.09
Nodes (42): Database, Base, FocusEvidence, FocusSession, Notification, Исключение из отображения расписания пользователя. exclusion_type: - "category"…, ScheduleExclusion, UserStats (+34 more)

### Community 52 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 53 - "Lesson"
Cohesion: 0.13
Nodes (23): get_schedule_exclusions(), lesson_is_excluded_by_category(), lesson_is_excluded_by_subject(), lesson_is_visible(), normalize_schedule_category(), normalize_schedule_value(), Get the user's schedule exclusions as sets of normalized category and subject…, Normalize a schedule value for comparison. Example: " Программирование " ->… (+15 more)

### Community 54 - "extends"
Cohesion: 0.50
Nodes (4): react-app, react-app/jest, eslintConfig, extends

### Community 56 - "_f"
Cohesion: 0.40
Nodes (6): ef(), _f(), Je(), qf(), Ue(), xf()

### Community 65 - "Phase 5 Audit Report"
Cohesion: 0.13
Nodes (14): A. Что проверено, B. Что найдено, C. Что изменено, D. Какие файлы изменены, E. API changes, F. Database changes, G. Evidence contract, H. Runtime tests (+6 more)

### Community 74 - "Phase 5 Verification Report"
Cohesion: 0.13
Nodes (14): Conclusion, Focus Completion Tests (`test_focus_completion.py`), Focus Evidence Tests (`test_focus_evidence.py`), ICS Parser Tests (`test_ics_parser.py`), Idempotency Verification, Overview, Phase 5 Verification Report, Phase 8 Requirements Verification (+6 more)

### Community 75 - "Текущая архитектура (монолит)"
Cohesion: 0.40
Nodes (4): Внешние зависимости, Основной файл: app/main.py, Структура пакетов, Текущая архитектура (монолит)

### Community 76 - "Phase 7 Audit Report"
Cohesion: 0.13
Nodes (14): Architecture, Async Flow, Changed, DB Session Safety, Error Handling, Events, HTTP Behavior, Idempotency (+6 more)

### Community 78 - "Phase 4 Audit Report"
Cohesion: 0.14
Nodes (13): A. Что проверено, B. Что найдено, C. Что изменено, D. Какие файлы изменены, E. API changes, F. Database changes, G. Runtime tests, H. Архитектурный аудит (+5 more)

### Community 79 - "Phase 9 Audit"
Cohesion: 0.14
Nodes (13): Anti-Farming Invariants, Concurrency Analysis, Duplicate Reward Analysis, Final Status, Lesson Occurrence Identity, Manual / AI Transition Analysis, Phase 9 Audit, Production Changes (+5 more)

### Community 81 - "LlamaCppClient"
Cohesion: 0.26
Nodes (5): get_llama_client(), LlamaCppClient, Any, Send a chat completion request to the llama.cpp server., Settings

### Community 87 - "bu"
Cohesion: 0.32
Nodes (12): ar(), Be(), bu(), Er(), gu(), ju(), ku(), lr() (+4 more)

### Community 94 - "LessonChange"
Cohesion: 0.18
Nodes (5): LessonChange, Результат сравнения одного занятия. kind: CREATED UPDATED MOVED DELETED…, Человекочитаемое описание изменения., GoogleCalendarServiceProtocol, Protocol

### Community 95 - "PHASE_8_STATUS.md"
Cohesion: 0.18
Nodes (10): Architecture, Changed, Duration / Confidence, Idempotency, Phase 8 Status, Remaining Issues, Reward Model, Sync / Import (+2 more)

### Community 96 - "create_test_lesson"
Cohesion: 0.18
Nodes (7): create_test_lesson(), create_test_user(), fixture, Helper to create a test user, Helper to create a test lesson, Create an in-memory SQLite database for testing, Create a database session

### Community 97 - "create_test_lesson"
Cohesion: 0.18
Nodes (7): create_test_lesson(), create_test_user(), fixture, Helper to create a test user, Helper to create a test lesson, Create an in-memory SQLite database for testing, Create a database session

### Community 98 - "RECOVERY AUDIT"
Cohesion: 0.22
Nodes (8): A. Git state, B. Phase status, C. Confirmed bugs, D. Route registration, E. Unfinished work, F. Changes from previous interrupted session, G. Recommended next step, RECOVERY AUDIT

### Community 99 - "export_to_obsidian"
Cohesion: 0.25
Nodes (8): delete_session(), export_to_obsidian(), get_current_user_info(), logout(), Any, Экспортируйте занятия в Obsidian., Log out the current user., Get the current user.

### Community 100 - "create_test_focus_session"
Cohesion: 0.25
Nodes (5): create_test_focus_session(), Test that concurrent manual completions of the same session do not award XP…, Test that concurrent AI verification processing does not award XP twice, Test that two focus sessions for the same lesson occurrence cannot both be…, Helper to create a focus session in the database

### Community 101 - "test_ai_verification_race_condition_postgres"
Cohesion: 0.29
Nodes (8): create_test_lesson(), create_test_user(), Test that concurrent AI verification processing does not award XP twice using…, Helper to create a test user, Helper to create a test lesson, Test that concurrent manual completions of the same session do not award XP…, test_ai_verification_race_condition_postgres(), test_manual_completion_race_condition_postgres()

### Community 102 - "PHASE 3B.3.1 RESULT"
Cohesion: 0.29
Nodes (6): Fix, PHASE 3B.3.1 RESULT, Regression, Root cause, Runtime, Verdict

### Community 103 - "PHASE 3B.3.2 — REPOSITORY STATE"
Cohesion: 0.29
Nodes (6): Current commits, Generated artifacts, PHASE 3B.3.2 — REPOSITORY STATE, Production changes, Ready state, Reports

### Community 104 - "PHASE 3B.3 RESULT"
Cohesion: 0.29
Nodes (6): A. Backend, B. Routes, C. Focus integration, D. Critical findings, E. Phase 3B.3, PHASE 3B.3 RESULT

### Community 105 - "PHASE_6_STATUS.md"
Cohesion: 0.29
Nodes (6): Architecture, Behavior, Changed, Phase 6 Status, Remaining Issues, Tests

### Community 106 - "PHASE_7_STATUS.md"
Cohesion: 0.29
Nodes (6): Architecture, Behavior, Changed, Phase 7 Status, Remaining Issues, Tests

### Community 107 - "create_session"
Cohesion: 0.33
Nodes (6): create_session(), Verify email using token from verification link., Reset password using token and new password., reset_password_endpoint(), verify_email(), AppSession

### Community 108 - "test_manual_completion_race_condition"
Cohesion: 0.33
Nodes (6): create_test_lesson(), create_test_user(), Helper to create a test user, Helper to create a test lesson, Debug version of the actual test, test_manual_completion_race_condition()

### Community 109 - "debug_manual_completion_race_condition"
Cohesion: 0.33
Nodes (6): create_test_lesson(), create_test_user(), debug_manual_completion_race_condition(), Helper to create a test user, Helper to create a test lesson, Debug version of the manual completion race condition test

### Community 110 - "Phase 25 — Tests"
Cohesion: 0.33
Nodes (6): Focus, Phase 25 — Tests, Schedule, Streak, Verification, XP

### Community 111 - "Phase 2 — Выделение существующих крупных доменов"
Cohesion: 0.50
Nodes (4): 2A. Stats, 2B. Gamification, Phase 2 — Выделение существующих крупных доменов, Но это ещё не финальная gamification-архитектура.

### Community 112 - "3B. Schedule Router Extraction"
Cohesion: 0.50
Nodes (4): 3B.1 — Route compatibility, 3B.2 — Focus → canonical Schedule filters, 3B.3 — Functional Schedule ↔ Focus integration, 3B. Schedule Router Extraction

### Community 113 - "Phase 6 — Verification / Local AI"
Cohesion: 0.67
Nodes (3): 6A. AI provider, 6B. Verification contract, Phase 6 — Verification / Local AI

### Community 114 - "Phase 8 — XP / Gamification redesign"
Cohesion: 0.67
Nodes (3): 8A. Manual completion, 8B. AI verified result, Phase 8 — XP / Gamification redesign

## Knowledge Gaps
- **277 isolated node(s):** `Config`, `short_name`, `name`, `icons`, `start_url` (+272 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `main.py`, `FocusService`, `telegram/service.py`, `sync/service.py`, `EmailService`, `post`, `mais_parser.py`, `.session`, `test_focus_race_condition.py`, `LessonData`, `cli.py`, `auth/schemas.py`, `get_token_path`, `Database`, `Lesson`, `LessonChange`, `create_test_lesson`, `create_test_lesson`, `export_to_obsidian`, `test_ai_verification_race_condition_postgres`, `test_manual_completion_race_condition`, `debug_manual_completion_race_condition`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `Lesson` connect `Lesson` to `calculate_diff`, `create_test_lesson`, `create_test_lesson`, `main.py`, `test_ai_verification_race_condition_postgres`, `FocusService`, `sync/service.py`, `test_manual_completion_race_condition`, `debug_manual_completion_race_condition`, `diff.py`, `User`, `Database`, `google_calendar/service.py`, `.session`, `test_focus_race_condition.py`, `LessonData`, `cli.py`, `LessonChange`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `FocusService` connect `FocusService` to `main.py`, `create_test_focus_session`, `test_ai_verification_race_condition_postgres`, `test_manual_completion_race_condition`, `debug_manual_completion_race_condition`, `User`, `Database`, `.session`, `Lesson`, `test_focus_race_condition.py`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `User` (e.g. with `FocusService` and `ObsidianPath`) actually correct?**
  _`User` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `l()` (e.g. with `H()` and `hf()`) actually correct?**
  _`l()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `FocusService` (e.g. with `VerificationResult` and `FocusEvidence`) actually correct?**
  _`FocusService` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Lesson` (e.g. with `FocusService` and `GoogleCalendarSyncService`) actually correct?**
  _`Lesson` has 15 INFERRED edges - model-reasoned connections that need verification._