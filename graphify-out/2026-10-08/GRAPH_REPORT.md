# Graph Report - XO_OS  (2026-10-08)

## Corpus Check
- 129 files · ~126,020 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1492 nodes · 3768 edges · 109 communities (87 shown, 22 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 351 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9d3f2c62`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.68c96a18.js
- l
- App.js
- main.py
- sync/service.py
- Ta
- FocusService
- telegram/routes.py
- Kc
- ii
- GoogleCalendarSyncService
- Yc
- rd
- roadmap.md
- TestFocusCompletion
- User Guide
- mais_parser.py
- auth/routes.py
- dependencies
- ⏳ Ожидают начала (Pending)
- google_calendar/routes.py
- StatsSection.js
- Database
- User
- i
- Learn More
- obsidian/routes.py
- Settings.js
- ._render_template
- EmailChangePage.jsx
- ScheduleList.js
- NowBlock.js
- Текущий статус реализации Google Calendar → XO_OS синхронизации
- .session
- PasswordResetPage.jsx
- IMPLEMENTATION STATUS: Google Calendar → XO_OS Sync
- PlanFact.js
- package.json
- Отчёт об интеграции уровня сохранения Google Calendar → XO_OS
- web/index.html
- devDependencies
- development
- web/manifest.json
- react-scripts
- .sync_changes
- public/manifest.json
- auth/schemas.py
- nc
- test_regression_final.py
- test_focus_race_condition.py
- bl
- test_postgres_concurrency.py
- scripts
- Lesson
- extends
- MAISync
- yi
- WeeklyChart.js
- test_persistence_integration.py
- MAISync logo (XO in black rounded rectangle)
- documentation
- README
- LessonData
- Текущая архитектура (монолит)
- _make_context
- MAISync
- FocusSession
- xo_os
- VerificationResult
- architecture-target.md
- focus.js
- service-boundaries.md
- stats/routes.py
- test_pagination_logic.py
- focus/routes.py
- ml
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
1. `User` - 93 edges
2. `l()` - 82 edges
3. `Database` - 73 edges
4. `FocusService` - 62 edges
5. `n()` - 61 edges
6. `i()` - 60 edges
7. `o()` - 59 edges
8. `ii()` - 50 edges
9. `Lesson` - 48 edges
10. `GoogleCalendarSyncService` - 44 edges

## Surprising Connections (you probably didn't know these)
- `TestFocusCompletion` --uses--> `VerificationResult`  [INFERRED]
  tests/test_focus_completion.py → app/ai/verification.py
- `TestFocusCompletionRaceCondition` --uses--> `VerificationResult`  [INFERRED]
  tests/test_focus_race_condition.py → app/ai/verification.py
- `TestFocusCompletion` --uses--> `AIVerificationService`  [INFERRED]
  tests/test_focus_completion.py → app/ai/verification.py
- `TestFocusCompletionRaceCondition` --uses--> `AIVerificationService`  [INFERRED]
  tests/test_focus_race_condition.py → app/ai/verification.py
- `TestFocusCompletion` --uses--> `Database`  [INFERRED]
  tests/test_focus_completion.py → app/database/db.py

## Import Cycles
- None detected.

## Communities (109 total, 22 thin omitted)

### Community 0 - "main.68c96a18.js"
Cohesion: 0.04
Nodes (62): ai(), al(), At(), bd(), Be(), bu(), cf(), ci() (+54 more)

### Community 1 - "l"
Cohesion: 0.16
Nodes (42): A(), as(), bs(), C(), cs(), d(), ds(), en() (+34 more)

### Community 2 - "App.js"
Cohesion: 0.11
Nodes (11): App(), Achievements(), CalendarObsidianBlock(), Header(), Login(), NextEvent(), Onboarding(), PlayerCard() (+3 more)

### Community 3 - "main.py"
Cohesion: 0.10
Nodes (13): health(), get, echo(), post, Request, event_publisher(), Publish events for a specific user., events_endpoint() (+5 more)

### Community 4 - "sync/service.py"
Cohesion: 0.05
Nodes (65): _build_identity_key(), _clean(), _detect_category(), LessonData, _parse_datetime(), _parse_description(), parse_ics(), Any (+57 more)

### Community 5 - "Ta"
Cohesion: 0.08
Nodes (16): af(), clear(), ea(), eject(), If(), ja(), lf(), ma() (+8 more)

### Community 6 - "FocusService"
Cohesion: 0.06
Nodes (30): FocusEvidence, FocusService, Session, Получите сеанс фокусировки по идентификатору, гарантируя, что он принадлежит…, Получите все доказательства для фокус-сессии., Проверка и подготовка доказательств к хранению. Возвращает кортеж (тип,…, Add evidence to a focus session., create_test_lesson() (+22 more)

### Community 7 - "telegram/routes.py"
Cohesion: 0.08
Nodes (45): TelegramLinkCode, error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files). (+37 more)

### Community 8 - "Kc"
Cohesion: 0.11
Nodes (43): ae(), au(), cu(), du(), ee(), et(), eu(), fu() (+35 more)

### Community 9 - "ii"
Cohesion: 0.08
Nodes (49): Aa(), Bo(), Br(), ca(), co(), De(), Do(), ei() (+41 more)

### Community 10 - "GoogleCalendarSyncService"
Cohesion: 0.12
Nodes (22): Base, GamificationLevel, GamificationXP, GoogleCalendarConnection, GoogleCalendarEvent, _event_to_lesson_key(), GoogleCalendarSyncService, Сохраняет события Google Calendar в локальную базу данных для данного… (+14 more)

### Community 11 - "Yc"
Cohesion: 0.14
Nodes (23): ar(), bf(), Dr(), ef(), _f(), Fe(), Gc(), gf() (+15 more)

### Community 12 - "rd"
Cohesion: 0.15
Nodes (18): ad(), An(), ao(), Cr(), Dn(), fr(), gt(), It() (+10 more)

### Community 13 - "roadmap.md"
Cohesion: 0.09
Nodes (22): Phase 10 — Real activity streak, Phase 11 — Gamification event architecture, Phase 12 — Auth extraction, Phase 13 — Email extraction, Phase 14 — Telegram extraction, Phase 15 — Sync extraction, Phase 16 — Google Calendar isolation, Phase 17 — MAIS parser isolation (+14 more)

### Community 14 - "TestFocusCompletion"
Cohesion: 0.05
Nodes (31): UserStats, XPTransaction, Наградите пользователя XP и обновите UserStats. Это вызывается, когда…, create_test_lesson(), create_test_user(), fixture, Test that manual completion doesn't award XP twice, Helper to create a test user (+23 more)

### Community 15 - "User Guide"
Cohesion: 0.09
Nodes (21): API Description, Architecture Overview, CLI Commands, Conflict Resolution, Dependencies, Environment Variables, License, Main Components (+13 more)

### Community 16 - "mais_parser.py"
Cohesion: 0.08
Nodes (28): check_mais_schedule_for_user(), Session, Check for schedule changes for a specific user and create notifications if…, async_fetch_group_schedule(), async_fetch_groups(), fetch_group_schedule(), fetch_groups(), _parse_date() (+20 more)

### Community 17 - "auth/routes.py"
Cohesion: 0.12
Nodes (43): confirm_email_change_endpoint(), initiate_email_change_endpoint(), initiate_password_reset_endpoint(), login(), logout(), post, Verify email using token from verification link., Resend verification email to user. (+35 more)

### Community 18 - "dependencies"
Cohesion: 0.10
Nodes (21): axios, react, react-dom, react-icons, react-router-dom, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+13 more)

### Community 19 - "⏳ Ожидают начала (Pending)"
Cohesion: 0.10
Nodes (19): Google Calendar → XO_OS Sync Progress Summary, 🔧 В процессе (In Progress), 🔗 Взаимодействие с существующим кодом, ✅ Выполнено (Completed), ⏳ Ожидают начала (Pending), 📝 Следующие шаги, 📊 Текущее состояние архитектуры, ЭТАП 10: Connection management (enable/disable) (+11 more)

### Community 20 - "google_calendar/routes.py"
Cohesion: 0.09
Nodes (35): get_calendar_status(), get, get_credentials_path(), get_data_dir(), get_google_calendar_service(), get_token_path(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file. (+27 more)

### Community 21 - "StatsSection.js"
Cohesion: 0.25
Nodes (6): COLORS, DonutChart(), formatNumber(), StatsSection(), formatNumber(), TopSubjects()

### Community 22 - "Database"
Cohesion: 0.08
Nodes (34): build_parser(), cmd_export(), cmd_import_ics(), cmd_stats(), cmd_status(), main(), Export lessons to Obsidian., Show user statistics. (+26 more)

### Community 23 - "User"
Cohesion: 0.12
Nodes (24): get_current_active_user(), User, post, Development-only endpoint to reset gamification data for the current user. This…, reset_gamification_endpoint(), get_gamification(), Session, Получите статистику геймификации текущего пользователя (уровень, опыт, серия).… (+16 more)

### Community 24 - "i"
Cohesion: 0.11
Nodes (44): ba(), bt(), constructor(), ct(), dd(), dt(), fd(), forEach() (+36 more)

### Community 25 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 26 - "obsidian/routes.py"
Cohesion: 0.19
Nodes (14): export_to_obsidian(), get_obsidian_path(), get_obsidian_status(), get_obsidian_vault_path(), ObsidianPath, Any, BaseModel, get (+6 more)

### Community 28 - "._render_template"
Cohesion: 0.20
Nodes (5): Отправьте электронное письмо для сброса пароля. Args: email: адрес электронной…, Отправьте электронное письмо с запросом подтверждения смены email. Args: email:…, Отправьте электронное письмо с подтверждением новой электронной почты. Args:…, Render a Jinja2 template with the given context. Args: template_name: Name of…, Отправьте электронное письмо с подтверждением регистрации. Args: email: адрес…

### Community 30 - "ScheduleList.js"
Cohesion: 0.40
Nodes (3): DEFAULT_CATEGORIES, getPluralForm(), ScheduleList()

### Community 31 - "NowBlock.js"
Cohesion: 0.14
Nodes (9): EMPTY_NOW, FocusState(), formatCurrentTime(), formatElapsedTime(), formatLessonType(), formatVerificationStatus(), LessonState(), NowBlock() (+1 more)

### Community 32 - "Текущий статус реализации Google Calendar → XO_OS синхронизации"
Cohesion: 0.22
Nodes (8): 🧪 Выполненные проверки:, ✅ Выполнено на данный момент:, 🎯 Следующие шаги по 12-этапному плану пользователя:, 💡 Текущая готовность к дальнейшей работе:, Текущий статус реализации Google Calendar → XO_OS синхронизации, 📝 Что НЕ было изменено (сознательное сохранение существующего поведения):, ЭТАП 1: Отделить FETCH / PERSIST / CONFLICT, ЭТАП 2: Google API Pagination

### Community 33 - ".session"
Cohesion: 0.11
Nodes (18): get_gamification(), get, put, Получите статистику геймификации текущего пользователя (уровень, опыт, серия).…, Обновите настройки геймификации для текущего пользователя. Сюда входят флаг…, update_gamification_settings(), start_background_tasks(), periodic_mais_check() (+10 more)

### Community 35 - "IMPLEMENTATION STATUS: Google Calendar → XO_OS Sync"
Cohesion: 0.25
Nodes (7): IMPLEMENTATION STATUS: Google Calendar → XO_OS Sync, 🏗️ АРХИТЕКТУРНЫЕ ПРИНЦИПЫ СОБЛЮДЕНЫ, 📊 ВЕРИФИКАЦИЯ, 📝 СВЯЗАННЫЕ ФАЙЛЫ, 🔧 СЛЕДУЮЩИЕ ЭТАПЫ (ПО ПЛАНУ ПОЛЬЗОВАТЕЛЯ), ✅ ЭТАП 1: ОТДЕЛИТЬ FETCH / PERSIST / CONFLICT - COMPLETED, ✅ ЭТАП 2: GOOGLE API PAGINATION - COMPLETED

### Community 36 - "PlanFact.js"
Cohesion: 0.33
Nodes (4): Sidebar(), FiCheck(), formatNumber(), PlanFact()

### Community 37 - "package.json"
Cohesion: 0.20
Nodes (9): author, description, keywords, license, main, name, private, proxy (+1 more)

### Community 38 - "Отчёт об интеграции уровня сохранения Google Calendar → XO_OS"
Cohesion: 0.14
Nodes (13): 1. Проверка импорта и синтаксиса, 2. Проверка создания FastAPI приложения, 3. Проверка существующих endpoints Google Calendar, 4. Специализированные тесты интеграции persistence, Архитектурные замечания, Выполненные проверки, Заключение, Конкретное изменение (+5 more)

### Community 40 - "devDependencies"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 41 - "development"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 42 - "web/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 44 - ".sync_changes"
Cohesion: 0.15
Nodes (12): _is_event_created_after_connection(), _lesson_to_google_event(), _parse_google_date_or_datetime(), datetime, LessonData, Преобразует объект Lesson или LessonData в словарь события Google Calendar., Получает события из целевого календаря Google Calendar. Возвращает список…, Обнаруживает события в Google Calendar, у которых нет соответствующего… (+4 more)

### Community 45 - "public/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 46 - "auth/schemas.py"
Cohesion: 0.18
Nodes (14): auth_status(), get_current_user_info(), Any, get, Get the current user., Check authentication status., AuthStatusResponse, Config (+6 more)

### Community 47 - "nc"
Cohesion: 0.33
Nodes (11): ac(), bi(), Cl(), ec(), fi(), ji(), nc(), rc() (+3 more)

### Community 48 - "test_regression_final.py"
Cohesion: 0.22
Nodes (12): create_mock_session(), Create a mock session that returns empty results for queries., Test that old style call does not throw TypeError., Test that new style call does not throw TypeError., Test that _fetch_google_events is called when google_events is None., Test that _fetch_google_events is NOT called when google_events is provided., Test that sync_changes can be called without TypeError and follows…, test_fetch_called_when_none() (+4 more)

### Community 49 - "test_focus_race_condition.py"
Cohesion: 0.22
Nodes (12): create_test_lesson(), create_test_user(), db(), fixture, Test suite for verifying race conditions in Focus completion, Helper to create a test user, Helper to create a test lesson, Create a file-based SQLite database for testing (+4 more)

### Community 51 - "test_postgres_concurrency.py"
Cohesion: 0.23
Nodes (12): create_test_focus_session(), create_test_lesson(), create_test_user(), PostgreSQL-based concurrency tests for Focus completion Uses real PostgreSQL…, Test that concurrent AI verification processing does not award XP twice using…, # NOTE: We use a regular Mock instead of AsyncMock to avoid coroutine issues in…, Helper to create a test user, Helper to create a test lesson (+4 more)

### Community 52 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 53 - "Lesson"
Cohesion: 0.11
Nodes (32): get_schedule_exclusions(), lesson_is_excluded_by_category(), lesson_is_excluded_by_subject(), lesson_is_visible(), normalize_schedule_category(), normalize_schedule_value(), Session, Get the user's schedule exclusions as sets of normalized category and subject… (+24 more)

### Community 54 - "extends"
Cohesion: 0.50
Nodes (4): react-app, react-app/jest, eslintConfig, extends

### Community 56 - "yi"
Cohesion: 0.60
Nodes (6): cc(), dc(), fc(), ic(), uc(), yi()

### Community 65 - "test_persistence_integration.py"
Cohesion: 0.18
Nodes (10): Test that all necessary modules can be imported., Test that we can create a service instance., Test that our new method exists., Test that _fetch_google_events still exists., Test that sync_changes still exists (we didn't modify it)., test_fetch_exists(), test_imports(), test_method_exists() (+2 more)

### Community 74 - "LessonData"
Cohesion: 0.50
Nodes (3): LessonData, datetime, This is a data transfer object for lesson data used in synchronization. It is…

### Community 75 - "Текущая архитектура (монолит)"
Cohesion: 0.40
Nodes (4): Внешние зависимости, Основной файл: app/main.py, Структура пакетов, Текущая архитектура (монолит)

### Community 79 - "FocusSession"
Cohesion: 0.10
Nodes (17): datetime, Единый источник времени для всего проекта., Aware UTC. Для ВСЕЙ логики: фокус-сессии, XP, фоновые задачи, транзакции,…, utc_now(), FocusSession, publish_focus_updated(), publish_gamification_updated(), Publish a focus session updated event to all connections for a user. (+9 more)

### Community 81 - "VerificationResult"
Cohesion: 0.13
Nodes (14): get_llama_client(), LlamaCppClient, Any, Send a chat completion request to the llama.cpp server. Повторяет запрос при…, fetch_url_text(), load_image_as_data_url(), Подготовка evidence к отправке в Qwen2.5-VL. Отвечает за: - обрезку текстовых…, Загружает страницу по URL и возвращает очищенный текст. Возвращает None, если… (+6 more)

### Community 94 - "stats/routes.py"
Cohesion: 0.18
Nodes (16): get_achievements(), get_plan_fact(), get_semester_stats(), get_top_subjects(), get_weekly_stats(), get, Загруженность по каждой неделе текущего семестра. Будущие недели возвращаются с…, Лучшие предметы по фактической учебной нагрузке в семестре. Фильтры применяются… (+8 more)

### Community 95 - "test_pagination_logic.py"
Cohesion: 0.40
Nodes (4): Test that the pagination logic is correctly implemented., Test that the method still works with time_min and time_max parameters., test_backward_compatibility(), test_pagination_logic()

### Community 96 - "focus/routes.py"
Cohesion: 0.09
Nodes (29): get_ai_verification_service(), add_evidence_to_focus_session(), _calculate_elapsed_seconds(), complete_focus_session(), get_active_focus_session(), get_focus_session(), pause_focus_session(), _process_ai_verification() (+21 more)

### Community 98 - "ml"
Cohesion: 0.16
Nodes (18): b(), dl(), _e(), fl(), G(), H(), Ha(), J() (+10 more)

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
- **175 isolated node(s):** `Config`, `short_name`, `name`, `icons`, `start_url` (+170 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `main.py`, `sync/service.py`, `FocusService`, `telegram/routes.py`, `GoogleCalendarSyncService`, `TestFocusCompletion`, `mais_parser.py`, `auth/routes.py`, `google_calendar/routes.py`, `Database`, `obsidian/routes.py`, `.session`, `auth/schemas.py`, `test_focus_race_condition.py`, `test_postgres_concurrency.py`, `Lesson`, `FocusSession`, `stats/routes.py`, `focus/routes.py`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `.session`, `test_persistence_integration.py`, `main.py`, `sync/service.py`, `FocusService`, `telegram/routes.py`, `GoogleCalendarSyncService`, `auth/schemas.py`, `FocusSession`, `test_regression_final.py`, `auth/routes.py`, `TestFocusCompletion`, `test_focus_race_condition.py`, `google_calendar/routes.py`, `test_postgres_concurrency.py`, `obsidian/routes.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `Lesson` connect `Lesson` to `focus/routes.py`, `sync/service.py`, `FocusService`, `GoogleCalendarSyncService`, `.sync_changes`, `TestFocusCompletion`, `FocusSession`, `test_focus_race_condition.py`, `test_postgres_concurrency.py`, `Database`, `stats/routes.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `FocusService` and `ObsidianPath`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `l()` (e.g. with `Aa()` and `_f()`) actually correct?**
  _`l()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `Database` (e.g. with `Base` and `GoogleCalendarSyncService`) actually correct?**
  _`Database` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `FocusService` (e.g. with `VerificationResult` and `FocusEvidence`) actually correct?**
  _`FocusService` has 7 INFERRED edges - model-reasoned connections that need verification._