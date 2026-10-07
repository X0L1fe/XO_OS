# Graph Report - XO_OS  (2026-10-07)

## Corpus Check
- 119 files · ~130,826 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1510 nodes · 3716 edges · 114 communities (93 shown, 21 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 333 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c1690990`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.68c96a18.js
- l
- App.js
- main.py
- sync/service.py
- hi
- FocusService
- telegram/routes.py
- Kc
- ii
- Database
- o
- google_calendar/routes.py
- roadmap.md
- auth/service.py
- User Guide
- mais_parser.py
- auth/routes.py
- dependencies
- test_focus_race_condition.py
- GoogleCalendarSyncService
- StatsSection.js
- Phase 6 Audit Report
- UserStats
- i
- Learn More
- obsidian/routes.py
- Settings.js
- Zo
- EmailChangePage.jsx
- ScheduleList.js
- NowBlock.js
- test_postgres_concurrency.py
- auth/schemas.py
- PasswordResetPage.jsx
- ._render_template
- PlanFact.js
- package.json
- config.py
- web/index.html
- devDependencies
- development
- web/manifest.json
- react-scripts
- check_mais_schedule_for_user
- public/manifest.json
- DEL_DATA.py
- nc
- Phase 8 Audit Report
- stats-router-extract.md
- bl
- TestFocusCompletion
- scripts
- Lesson
- extends
- MAISync
- yi
- WeeklyChart.js
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
- VerificationResult
- architecture-target.md
- focus.js
- service-boundaries.md
- User
- PHASE_8_STATUS.md
- add_evidence_to_focus_session
- logout
- RECOVERY AUDIT
- PHASE 3B.3.1 RESULT
- PHASE 3B.3.2 — REPOSITORY STATE
- PHASE 3B.3 RESULT
- PHASE_6_STATUS.md
- PHASE_7_STATUS.md
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
1. `User` - 88 edges
2. `l()` - 82 edges
3. `FocusService` - 64 edges
4. `n()` - 61 edges
5. `i()` - 60 edges
6. `o()` - 59 edges
7. `Database` - 50 edges
8. `ii()` - 50 edges
9. `Lesson` - 49 edges
10. `ml()` - 29 edges

## Surprising Connections (you probably didn't know these)
- `TestFocusCompletion` --uses--> `VerificationResult`  [INFERRED]
  tests/test_focus_completion.py → app/ai/verification.py
- `TestFocusCompletion` --uses--> `AIVerificationService`  [INFERRED]
  tests/test_focus_completion.py → app/ai/verification.py
- `TestFocusCompletion` --uses--> `Database`  [INFERRED]
  tests/test_focus_completion.py → app/database/db.py
- `TestFocusEvidence` --uses--> `Database`  [INFERRED]
  tests/test_focus_evidence.py → app/database/db.py
- `TestFocusCompletionRaceCondition` --uses--> `Database`  [INFERRED]
  tests/test_focus_race_condition.py → app/database/db.py

## Import Cycles
- None detected.

## Communities (114 total, 21 thin omitted)

### Community 0 - "main.68c96a18.js"
Cohesion: 0.05
Nodes (45): ai(), al(), ar(), At(), bu(), cf(), componentDidCatch(), df() (+37 more)

### Community 1 - "l"
Cohesion: 0.07
Nodes (68): A(), ad(), An(), ao(), b(), bf(), co(), d() (+60 more)

### Community 2 - "App.js"
Cohesion: 0.11
Nodes (11): App(), Achievements(), CalendarObsidianBlock(), Header(), Login(), NextEvent(), Onboarding(), PlayerCard() (+3 more)

### Community 3 - "main.py"
Cohesion: 0.10
Nodes (28): event_publisher(), Publish events for a specific user., complete_onboarding(), echo(), events_endpoint(), get_calendar_status(), get_mais_groups(), get_notifications() (+20 more)

### Community 4 - "sync/service.py"
Cohesion: 0.05
Nodes (66): _build_identity_key(), _clean(), _detect_category(), LessonData, _parse_datetime(), _parse_description(), parse_ics(), Any (+58 more)

### Community 5 - "hi"
Cohesion: 0.06
Nodes (29): af(), bd(), ci(), clear(), di(), ea(), eject(), ga() (+21 more)

### Community 6 - "FocusService"
Cohesion: 0.04
Nodes (43): Aware UTC. Для ВСЕЙ логики: фокус-сессии, XP, фоновые задачи, транзакции,…, utc_now(), FocusEvidence, FocusSession, publish_focus_updated(), Publish a focus session updated event to all connections for a user., FocusService, Resume a paused focus session. (+35 more)

### Community 7 - "telegram/routes.py"
Cohesion: 0.08
Nodes (45): TelegramLinkCode, error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files). (+37 more)

### Community 8 - "Kc"
Cohesion: 0.09
Nodes (50): ae(), au(), Be(), cu(), dt(), du(), ee(), eu() (+42 more)

### Community 9 - "ii"
Cohesion: 0.16
Nodes (25): Aa(), Bo(), ca(), Do(), El(), Fa(), Go(), ia() (+17 more)

### Community 10 - "Database"
Cohesion: 0.12
Nodes (20): build_parser(), cmd_export(), cmd_import_ics(), cmd_stats(), cmd_status(), main(), Export lessons to Obsidian., Show user statistics. (+12 more)

### Community 11 - "o"
Cohesion: 0.13
Nodes (36): as(), bs(), C(), cs(), Dn(), ds(), en(), fs() (+28 more)

### Community 12 - "google_calendar/routes.py"
Cohesion: 0.12
Nodes (25): get_credentials_path(), get_data_dir(), get_google_calendar_service(), get_token_path(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., Returns the path to the Google OAuth2 token file., Authenticates with Google Calendar API and returns a service object. Handles… (+17 more)

### Community 13 - "roadmap.md"
Cohesion: 0.09
Nodes (22): Phase 10 — Real activity streak, Phase 11 — Gamification event architecture, Phase 12 — Auth extraction, Phase 13 — Email extraction, Phase 14 — Telegram extraction, Phase 15 — Sync extraction, Phase 16 — Google Calendar isolation, Phase 17 — MAIS parser isolation (+14 more)

### Community 14 - "auth/service.py"
Cohesion: 0.18
Nodes (16): authenticate_user(), confirm_email_change(), delete_session(), get_current_active_user(), get_current_user(), get_user_from_session(), _make_context(), SQLAlchemySession (+8 more)

### Community 15 - "User Guide"
Cohesion: 0.09
Nodes (21): API Description, Architecture Overview, CLI Commands, Conflict Resolution, Dependencies, Environment Variables, License, Main Components (+13 more)

### Community 16 - "mais_parser.py"
Cohesion: 0.18
Nodes (12): import_mais_schedule(), Import schedule for a given MAIS group name., async_fetch_groups(), fetch_group_schedule(), _parse_date(), parse_mais_schedule(), _parse_time(), Fetch schedule JSON for a given group name. Uses MD5 of group name as the… (+4 more)

### Community 17 - "auth/routes.py"
Cohesion: 0.16
Nodes (28): confirm_email_change_endpoint(), initiate_email_change_endpoint(), initiate_password_reset_endpoint(), login(), post, Verify email using token from verification link., Resend verification email to user., Initiate password reset process. (+20 more)

### Community 18 - "dependencies"
Cohesion: 0.10
Nodes (21): axios, react, react-dom, react-icons, react-router-dom, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+13 more)

### Community 19 - "test_focus_race_condition.py"
Cohesion: 0.14
Nodes (18): get_ai_verification_service(), complete_focus_session(), _process_ai_verification(), BackgroundTasks, Завершите фокус-сессию. Если для режима завершения выбрано значение «ручной»,…, Фоновая проверка evidence через AI и начисление XP. Все зависимости создаются…, create_test_lesson(), create_test_user() (+10 more)

### Community 20 - "GoogleCalendarSyncService"
Cohesion: 0.21
Nodes (8): GoogleCalendarSyncService, _lesson_to_google_event(), datetime, Получает события из целевого календаря Google Calendar. Возвращает список…, Обнаруживает события в Google Calendar, у которых нет соответствующего…, Синхронизирует изменения (созданные, обновленные, удаленные, перемещенные) в…, Преобразует объект Lesson или LessonData в словарь события Google Calendar., Синхронизируйте один урок с Календарем Google (создайте или обновите).…

### Community 21 - "StatsSection.js"
Cohesion: 0.25
Nodes (6): COLORS, DonutChart(), formatNumber(), StatsSection(), formatNumber(), TopSubjects()

### Community 22 - "Phase 6 Audit Report"
Cohesion: 0.11
Nodes (18): A. Что проверено, B. Текущий AI architecture, C. AI request flow, D. AI response flow, E. VerificationResult contract, F. FocusSession verification lifecycle, G. FocusEvidence → AI integration, H. XP integration (+10 more)

### Community 23 - "UserStats"
Cohesion: 0.16
Nodes (13): Base, Session, UserStats, post, Development-only endpoint to reset gamification data for the current user. This…, reset_gamification_endpoint(), get_gamification(), Получите статистику геймификации текущего пользователя (уровень, опыт, серия).… (+5 more)

### Community 24 - "i"
Cohesion: 0.11
Nodes (44): ba(), bt(), constructor(), Cr(), ct(), dd(), fd(), forEach() (+36 more)

### Community 25 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 26 - "obsidian/routes.py"
Cohesion: 0.19
Nodes (14): export_to_obsidian(), get_obsidian_path(), get_obsidian_status(), get_obsidian_vault_path(), ObsidianPath, Any, BaseModel, get (+6 more)

### Community 28 - "Zo"
Cohesion: 0.16
Nodes (18): Br(), De(), ei(), gr(), hf(), If(), Jo(), Kr() (+10 more)

### Community 30 - "ScheduleList.js"
Cohesion: 0.40
Nodes (3): DEFAULT_CATEGORIES, getPluralForm(), ScheduleList()

### Community 31 - "NowBlock.js"
Cohesion: 0.14
Nodes (9): EMPTY_NOW, FocusState(), formatCurrentTime(), formatElapsedTime(), formatLessonType(), formatVerificationStatus(), LessonState(), NowBlock() (+1 more)

### Community 32 - "test_postgres_concurrency.py"
Cohesion: 0.21
Nodes (13): XPTransaction, create_test_focus_session(), create_test_lesson(), create_test_user(), PostgreSQL-based concurrency tests for Focus completion Uses real PostgreSQL…, Test that concurrent AI verification processing does not award XP twice using…, # NOTE: We use a regular Mock instead of AsyncMock to avoid coroutine issues in…, Helper to create a test user (+5 more)

### Community 33 - "auth/schemas.py"
Cohesion: 0.27
Nodes (10): auth_status(), Check authentication status., AuthStatusResponse, Config, BaseModel, TokenResponse, UserBase, UserCreate (+2 more)

### Community 35 - "._render_template"
Cohesion: 0.20
Nodes (5): Отправьте электронное письмо для сброса пароля. Args: email: адрес электронной…, Отправьте электронное письмо с запросом подтверждения смены email. Args: email:…, Отправьте электронное письмо с подтверждением новой электронной почты. Args:…, Render a Jinja2 template with the given context. Args: template_name: Name of…, Отправьте электронное письмо с подтверждением регистрации. Args: email: адрес…

### Community 36 - "PlanFact.js"
Cohesion: 0.33
Nodes (4): Sidebar(), FiCheck(), formatNumber(), PlanFact()

### Community 37 - "package.json"
Cohesion: 0.20
Nodes (9): author, description, keywords, license, main, name, private, proxy (+1 more)

### Community 38 - "config.py"
Cohesion: 0.28
Nodes (4): get_llama_client(), LlamaCppClient, Any, Send a chat completion request to the llama.cpp server. Повторяет запрос при…

### Community 40 - "devDependencies"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 41 - "development"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 42 - "web/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 44 - "check_mais_schedule_for_user"
Cohesion: 0.22
Nodes (9): Notification, check_mais_schedule_for_user(), periodic_mais_check(), Check for schedule changes for a specific user and create notifications if…, Background task that periodically checks for MAIS schedule changes for all…, start_background_tasks(), async_fetch_group_schedule(), Fetch schedule JSON for a given group name asynchronously. Uses MD5 of group… (+1 more)

### Community 45 - "public/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 46 - "DEL_DATA.py"
Cohesion: 0.33
Nodes (8): clear_calendar(), _delete_callback(), get_calendar_service(), get_event_ids_from_db(), main(), Возвращает авторизованный сервис Google Calendar., Достаёт все непустые google_event_id из таблицы lessons., Пакетно удаляет события из указанного календаря.

### Community 47 - "nc"
Cohesion: 0.33
Nodes (11): ac(), bi(), Cl(), ec(), fi(), ji(), nc(), rc() (+3 more)

### Community 48 - "Phase 8 Audit Report"
Cohesion: 0.12
Nodes (15): AI verified completion:, Current Focus Reward Flow, Current Gamification Events, Current Level Usage, Current Streak Usage, Current XP Formula, Current XP Sources, Current XPTransaction Usage (+7 more)

### Community 49 - "stats-router-extract.md"
Cohesion: 0.22
Nodes (7): Changes, Files Created, Files Modified, How to Apply, Summary, Verification, Why

### Community 51 - "TestFocusCompletion"
Cohesion: 0.08
Nodes (22): publish_gamification_updated(), Publish a gamification updated event to all connections for a user., create_test_lesson(), create_test_user(), fixture, Test suite for verifying Focus completion and AI verification functionality…, Test that manual completion doesn't award XP twice, Helper to create a test user (+14 more)

### Community 52 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 53 - "Lesson"
Cohesion: 0.13
Nodes (29): get_schedule_exclusions(), lesson_is_excluded_by_category(), lesson_is_excluded_by_subject(), lesson_is_visible(), normalize_schedule_category(), normalize_schedule_value(), Get the user's schedule exclusions as sets of normalized category and subject…, Normalize a schedule value for comparison. Example: " Программирование " ->… (+21 more)

### Community 54 - "extends"
Cohesion: 0.50
Nodes (4): react-app, react-app/jest, eslintConfig, extends

### Community 56 - "yi"
Cohesion: 0.60
Nodes (6): cc(), dc(), fc(), ic(), uc(), yi()

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

### Community 81 - "VerificationResult"
Cohesion: 0.10
Nodes (18): fetch_url_text(), load_image_as_data_url(), Подготовка evidence к отправке в Qwen2.5-VL. Отвечает за: - обрезку текстовых…, Загружает страницу по URL и возвращает очищенный текст. Возвращает None, если…, Читает картинку из MEDIA_ROOT/<rel_path>, ресайзит и возвращает…, truncate_text(), AIVerificationService, Any (+10 more)

### Community 94 - "User"
Cohesion: 0.07
Nodes (49): User, _calculate_elapsed_seconds(), get_active_focus_session(), get_focus_session(), pause_focus_session(), get, post, Resume a paused focus session. (+41 more)

### Community 95 - "PHASE_8_STATUS.md"
Cohesion: 0.18
Nodes (10): Architecture, Changed, Duration / Confidence, Idempotency, Phase 8 Status, Remaining Issues, Reward Model, Sync / Import (+2 more)

### Community 96 - "add_evidence_to_focus_session"
Cohesion: 0.25
Nodes (8): add_evidence_to_focus_session(), Добавляет evidence к фокус-сессии. Принимает multipart/form-data: - text:…, delete_evidence_image(), Хранилище файлов evidence. Отвечает только за файловую систему: сохранение,…, Сохраняет изображение evidence на диск. Возвращает путь относительно…, Удаляет файл evidence, если он существует. Ошибки игнорируются (файл может быть…, save_evidence_image(), UploadFile

### Community 97 - "logout"
Cohesion: 0.33
Nodes (6): get_current_user_info(), logout(), Any, get, Log out the current user., Get the current user.

### Community 98 - "RECOVERY AUDIT"
Cohesion: 0.22
Nodes (8): A. Git state, B. Phase status, C. Confirmed bugs, D. Route registration, E. Unfinished work, F. Changes from previous interrupted session, G. Recommended next step, RECOVERY AUDIT

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
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `main.py`, `sync/service.py`, `FocusService`, `telegram/routes.py`, `Database`, `google_calendar/routes.py`, `auth/service.py`, `mais_parser.py`, `auth/routes.py`, `test_focus_race_condition.py`, `UserStats`, `obsidian/routes.py`, `test_postgres_concurrency.py`, `auth/schemas.py`, `check_mais_schedule_for_user`, `TestFocusCompletion`, `Lesson`, `VerificationResult`, `add_evidence_to_focus_session`, `logout`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `Lesson` connect `Lesson` to `test_postgres_concurrency.py`, `main.py`, `sync/service.py`, `FocusService`, `Database`, `google_calendar/routes.py`, `VerificationResult`, `TestFocusCompletion`, `GoogleCalendarSyncService`, `test_focus_race_condition.py`, `UserStats`, `User`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `FocusService` connect `FocusService` to `add_evidence_to_focus_session`, `test_postgres_concurrency.py`, `main.py`, `VerificationResult`, `test_focus_race_condition.py`, `TestFocusCompletion`, `Lesson`, `UserStats`, `User`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `FocusService` and `ObsidianPath`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `l()` (e.g. with `Aa()` and `_f()`) actually correct?**
  _`l()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `FocusService` (e.g. with `VerificationResult` and `FocusEvidence`) actually correct?**
  _`FocusService` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `n()` (e.g. with `A()` and `ad()`) actually correct?**
  _`n()` has 44 INFERRED edges - model-reasoned connections that need verification._