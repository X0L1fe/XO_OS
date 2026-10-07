# Graph Report - XO_OS  (2026-10-05)

## Corpus Check
- 115 files · ~131,666 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1518 nodes · 3751 edges · 124 communities (99 shown, 25 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 342 edges (avg confidence: 0.53)
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
- parse_ics
- Ta
- FocusService
- telegram/service.py
- Kc
- ii
- sync/service.py
- ._render_template
- post
- roadmap.md
- diff.py
- User Guide
- mais_parser.py
- auth/routes.py
- dependencies
- focus/routes.py
- google_calendar/service.py
- StatsSection.js
- Phase 6 Audit Report
- create_test_lesson
- _t
- Learn More
- Database
- Settings.js
- Yc
- EmailChangePage.jsx
- ScheduleList.js
- NowBlock.js
- calculate_diff
- utc_now
- PasswordResetPage.jsx
- TestFocusCompletion
- PlanFact.js
- package.json
- create_user
- web/index.html
- devDependencies
- development
- web/manifest.json
- react-scripts
- telegram_link
- public/manifest.json
- get_token_path
- nc
- Phase 8 Audit Report
- stats-router-extract.md
- bl
- User
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
- AIVerificationService
- architecture-target.md
- focus.js
- service-boundaries.md
- .session
- PHASE_8_STATUS.md
- ml
- EmailService
- RECOVERY AUDIT
- events_endpoint
- LlamaCppClient
- test_ai_verification_race_condition_postgres
- PHASE 3B.3.1 RESULT
- PHASE 3B.3.2 — REPOSITORY STATE
- PHASE 3B.3 RESULT
- PHASE_6_STATUS.md
- PHASE_7_STATUS.md
- auth_status
- check_mais_schedule_for_user
- export_to_obsidian
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
- .content_hash
- .stable_id
- .description
- .get_stats

## God Nodes (most connected - your core abstractions)
1. `User` - 90 edges
2. `l()` - 82 edges
3. `FocusService` - 64 edges
4. `n()` - 61 edges
5. `i()` - 60 edges
6. `o()` - 59 edges
7. `ii()` - 50 edges
8. `Lesson` - 49 edges
9. `Database` - 47 edges
10. `ml()` - 29 edges

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

## Communities (124 total, 25 thin omitted)

### Community 0 - "main.68c96a18.js"
Cohesion: 0.04
Nodes (74): ai(), al(), An(), ar(), At(), bd(), bu(), cf() (+66 more)

### Community 1 - "l"
Cohesion: 0.14
Nodes (61): A(), ad(), as(), b(), bs(), C(), cs(), d() (+53 more)

### Community 2 - "App.js"
Cohesion: 0.11
Nodes (11): App(), Achievements(), CalendarObsidianBlock(), Header(), Login(), NextEvent(), Onboarding(), PlayerCard() (+3 more)

### Community 3 - "main.py"
Cohesion: 0.09
Nodes (29): auth_status(), get_achievements(), get_google_calendars(), get_notifications(), get_obsidian_status(), google_auth(), google_status(), health() (+21 more)

### Community 4 - "parse_ics"
Cohesion: 0.11
Nodes (28): _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), Any, datetime (+20 more)

### Community 5 - "Ta"
Cohesion: 0.11
Nodes (8): af(), ea(), lf(), ma(), Qi(), sa(), Ta(), xi()

### Community 6 - "FocusService"
Cohesion: 0.05
Nodes (27): FocusService, Получите сеанс активного фокуса для пользователя, если таковой имеется., Получите текущий незавершенный сеанс фокусировки для пользователя. Текущая…, Получите сеанс фокусировки по идентификатору, гарантируя, что он принадлежит…, Получите все доказательства для фокус-сессии., Проверка и подготовка доказательств к хранению. Возвращает кортеж (тип,…, Add evidence to a focus session., create_test_lesson() (+19 more)

### Community 7 - "telegram/service.py"
Cohesion: 0.12
Nodes (29): TelegramLinkCode, error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files). (+21 more)

### Community 8 - "Kc"
Cohesion: 0.09
Nodes (47): ae(), au(), Be(), cu(), du(), ee(), eu(), fu() (+39 more)

### Community 9 - "ii"
Cohesion: 0.15
Nodes (29): Aa(), Bo(), Do(), El(), Fa(), Go(), ia(), ii() (+21 more)

### Community 10 - "sync/service.py"
Cohesion: 0.15
Nodes (18): LessonData, Нормализованное занятие MAISync. source_uid: Оригинальный UID из ICS. Сохраняем…, DiffResult, LessonChange, Результат сравнения одного занятия. kind: CREATED UPDATED MOVED DELETED…, _apply_lesson_data(), _create_lesson(), GoogleCalendarServiceProtocol (+10 more)

### Community 11 - "._render_template"
Cohesion: 0.20
Nodes (5): Отправьте электронное письмо для сброса пароля. Args: email: адрес электронной…, Отправьте электронное письмо с запросом подтверждения смены email. Args: email:…, Отправьте электронное письмо с подтверждением новой электронной почты. Args:…, Render a Jinja2 template with the given context. Args: template_name: Name of…, Отправьте электронное письмо с подтверждением регистрации. Args: email: адрес…

### Community 12 - "post"
Cohesion: 0.16
Nodes (18): create_session(), confirm_email_change_endpoint(), initiate_email_change_endpoint(), initiate_password_reset_endpoint(), login(), logout(), post, Response (+10 more)

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
Cohesion: 0.13
Nodes (16): get_mais_groups(), import_mais_schedule(), Get list of MAIS groups., Import schedule for a given MAIS group name., async_fetch_groups(), fetch_group_schedule(), fetch_groups(), _parse_date() (+8 more)

### Community 17 - "auth/routes.py"
Cohesion: 0.21
Nodes (20): authenticate_user(), confirm_email_change(), delete_session(), get_current_user(), get_password_hash(), get_user_from_session(), initiate_email_change(), initiate_password_reset() (+12 more)

### Community 18 - "dependencies"
Cohesion: 0.10
Nodes (21): axios, react, react-dom, react-icons, react-router-dom, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+13 more)

### Community 19 - "focus/routes.py"
Cohesion: 0.08
Nodes (36): get_ai_verification_service(), VerificationResult, publish_focus_updated(), publish_gamification_updated(), Publish a focus session updated event to all connections for a user., Publish a gamification updated event to all connections for a user., add_evidence_to_focus_session(), _calculate_elapsed_seconds() (+28 more)

### Community 20 - "google_calendar/service.py"
Cohesion: 0.17
Nodes (12): get_google_calendar_service(), Authenticates with Google Calendar API and returns a service object. Handles…, _event_to_lesson_key(), GoogleCalendarSyncService, _lesson_to_google_event(), datetime, Получает события из целевого календаря Google Calendar. Возвращает список…, Обнаруживает события в Google Calendar, у которых нет соответствующего… (+4 more)

### Community 21 - "StatsSection.js"
Cohesion: 0.25
Nodes (6): COLORS, DonutChart(), formatNumber(), StatsSection(), formatNumber(), TopSubjects()

### Community 22 - "Phase 6 Audit Report"
Cohesion: 0.11
Nodes (18): A. Что проверено, B. Текущий AI architecture, C. AI request flow, D. AI response flow, E. VerificationResult contract, F. FocusSession verification lifecycle, G. FocusEvidence → AI integration, H. XP integration (+10 more)

### Community 23 - "create_test_lesson"
Cohesion: 0.25
Nodes (8): create_test_lesson(), db(), fixture, Helper to create a test lesson, Create a file-based SQLite database for testing, Create a database session, session(), test_lesson()

### Community 24 - "_t"
Cohesion: 0.09
Nodes (47): ba(), bt(), constructor(), Cr(), ct(), dd(), dt(), ef() (+39 more)

### Community 25 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 26 - "Database"
Cohesion: 0.19
Nodes (15): build_parser(), cmd_export(), cmd_import_ics(), cmd_stats(), cmd_status(), main(), Export lessons to Obsidian., Show user statistics. (+7 more)

### Community 28 - "Yc"
Cohesion: 0.13
Nodes (24): ao(), bf(), co(), Fe(), fo(), Gc(), gf(), ho() (+16 more)

### Community 30 - "ScheduleList.js"
Cohesion: 0.40
Nodes (3): DEFAULT_CATEGORIES, getPluralForm(), ScheduleList()

### Community 31 - "NowBlock.js"
Cohesion: 0.14
Nodes (9): EMPTY_NOW, FocusState(), formatCurrentTime(), formatElapsedTime(), formatLessonType(), formatVerificationStatus(), LessonState(), NowBlock() (+1 more)

### Community 32 - "calculate_diff"
Cohesion: 0.53
Nodes (9): calculate_diff(), Сравнивает старое состояние с новым. Алгоритм: 1. Exact match по identity_key.…, make_new(), make_old(), test_date_change_is_moved(), test_exact_identity_is_updated(), test_new_lesson_is_created(), test_time_change_is_moved() (+1 more)

### Community 33 - "utc_now"
Cohesion: 0.13
Nodes (10): datetime, Единый источник времени для всего проекта., Aware UTC. Для ВСЕЙ логики: фокус-сессии, XP, фоновые задачи, транзакции,…, utc_now(), Resume a paused focus session., Завершите фокус-сессию. Если для завершения_режима установлено значение…, Наградите пользователя XP и обновите UserStats. Это вызывается, когда…, Start a new focus session for the user. The backend determines the current… (+2 more)

### Community 35 - "TestFocusCompletion"
Cohesion: 0.09
Nodes (19): create_test_lesson(), create_test_user(), fixture, Test that manual completion doesn't award XP twice, Helper to create a test user, Test that AI verified completion with score 0.0 awards 10 XP, Test that AI verified completion with score 0.5 awards 15 XP, Test that AI verified completion with score 1.0 awards 20 XP (+11 more)

### Community 36 - "PlanFact.js"
Cohesion: 0.33
Nodes (4): Sidebar(), FiCheck(), formatNumber(), PlanFact()

### Community 37 - "package.json"
Cohesion: 0.20
Nodes (9): author, description, keywords, license, main, name, private, proxy (+1 more)

### Community 38 - "create_user"
Cohesion: 0.29
Nodes (10): AuthStatusResponse, Config, BaseModel, TokenResponse, UserBase, UserCreate, UserLogin, UserResponse (+2 more)

### Community 40 - "devDependencies"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 41 - "development"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 42 - "web/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 44 - "telegram_link"
Cohesion: 0.22
Nodes (10): Создаёт одноразовый код привязки учетной записи Telegram и создаёт Telegram…, Return Telegram connection status., Unlink Telegram account., telegram_link(), telegram_status(), telegram_unlink(), BaseModel, TelegramLinkResponse (+2 more)

### Community 45 - "public/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 46 - "get_token_path"
Cohesion: 0.14
Nodes (19): get_credentials_path(), get_data_dir(), get_token_path(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., Returns the path to the Google OAuth2 token file., get_calendar_status(), google_callback() (+11 more)

### Community 47 - "nc"
Cohesion: 0.33
Nodes (11): ac(), bi(), Cl(), ec(), fi(), ji(), nc(), rc() (+3 more)

### Community 48 - "Phase 8 Audit Report"
Cohesion: 0.12
Nodes (15): AI verified completion:, Current Focus Reward Flow, Current Gamification Events, Current Level Usage, Current Streak Usage, Current XP Formula, Current XP Sources, Current XPTransaction Usage (+7 more)

### Community 49 - "stats-router-extract.md"
Cohesion: 0.22
Nodes (7): Changes, Files Created, Files Modified, How to Apply, Summary, Verification, Why

### Community 51 - "User"
Cohesion: 0.09
Nodes (41): get_current_active_user(), Base, FocusEvidence, FocusSession, Notification, Исключение из отображения расписания пользователя. exclusion_type: - "category"…, ScheduleExclusion, Session (+33 more)

### Community 52 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 53 - "Lesson"
Cohesion: 0.10
Nodes (31): get_schedule_exclusions(), lesson_is_excluded_by_category(), lesson_is_excluded_by_subject(), lesson_is_visible(), normalize_schedule_category(), normalize_schedule_value(), Get the user's schedule exclusions as sets of normalized category and subject…, Normalize a schedule value for comparison. Example: " Программирование " ->… (+23 more)

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

### Community 81 - "AIVerificationService"
Cohesion: 0.18
Nodes (9): fetch_url_text(), load_image_as_data_url(), Подготовка evidence к отправке в Qwen2.5-VL. Отвечает за: - обрезку текстовых…, Загружает страницу по URL и возвращает очищенный текст. Возвращает None, если…, Читает картинку из MEDIA_ROOT/<rel_path>, ресайзит и возвращает…, truncate_text(), AIVerificationService, Any (+1 more)

### Community 94 - ".session"
Cohesion: 0.13
Nodes (26): msk_now_naive(), Naive MSK. ТОЛЬКО для сравнения с Lesson.start_time / Lesson.end_time, которые…, get_gamification(), get, put, Получите статистику геймификации текущего пользователя (уровень, опыт, серия).…, Обновите настройки геймификации для текущего пользователя. Сюда входят флаг…, update_gamification_settings() (+18 more)

### Community 95 - "PHASE_8_STATUS.md"
Cohesion: 0.18
Nodes (10): Architecture, Changed, Duration / Confidence, Idempotency, Phase 8 Status, Remaining Issues, Reward Model, Sync / Import (+2 more)

### Community 96 - "ml"
Cohesion: 0.13
Nodes (25): Br(), ca(), De(), dl(), ei(), fl(), ga(), gr() (+17 more)

### Community 97 - "EmailService"
Cohesion: 0.19
Nodes (19): confirm_email_change_endpoint(), initiate_email_change_endpoint(), initiate_password_reset_endpoint(), login(), logout(), post, Response, Resend verification email to user. (+11 more)

### Community 98 - "RECOVERY AUDIT"
Cohesion: 0.22
Nodes (8): A. Git state, B. Phase status, C. Confirmed bugs, D. Route registration, E. Unfinished work, F. Changes from previous interrupted session, G. Recommended next step, RECOVERY AUDIT

### Community 99 - "events_endpoint"
Cohesion: 0.15
Nodes (13): event_publisher(), Publish events for a specific user., complete_onboarding(), echo(), events_endpoint(), BackgroundTasks, Complete onboarding by saving group and calendar selection., Save the user's selected Google Calendar ID for synchronization. (+5 more)

### Community 100 - "LlamaCppClient"
Cohesion: 0.28
Nodes (4): get_llama_client(), LlamaCppClient, Any, Send a chat completion request to the llama.cpp server. Повторяет запрос при…

### Community 101 - "test_ai_verification_race_condition_postgres"
Cohesion: 0.24
Nodes (10): create_test_focus_session(), create_test_lesson(), create_test_user(), Test that concurrent AI verification processing does not award XP twice using…, Helper to create a test user, Helper to create a test lesson, Helper to create a focus session in the database, Test that concurrent manual completions of the same session do not award XP… (+2 more)

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

### Community 107 - "auth_status"
Cohesion: 0.25
Nodes (8): auth_status(), get_current_user_info(), Any, get, Verify email using token from verification link., Get the current user., Check authentication status., verify_email()

### Community 108 - "check_mais_schedule_for_user"
Cohesion: 0.25
Nodes (8): check_mais_schedule_for_user(), periodic_mais_check(), Check for schedule changes for a specific user and create notifications if…, Background task that periodically checks for MAIS schedule changes for all…, start_background_tasks(), async_fetch_group_schedule(), Fetch schedule JSON for a given group name asynchronously. Uses MD5 of group…, on_event

### Community 109 - "export_to_obsidian"
Cohesion: 0.25
Nodes (8): export_to_obsidian(), get_current_user_info(), get_obsidian_path(), get_obsidian_vault_path(), Any, Экспортируйте занятия в Obsidian., Get the current user., Get saved Obsidian vault path.

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
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `main.py`, `FocusService`, `telegram/service.py`, `sync/service.py`, `post`, `mais_parser.py`, `auth/routes.py`, `focus/routes.py`, `Database`, `TestFocusCompletion`, `create_user`, `telegram_link`, `Lesson`, `.session`, `EmailService`, `events_endpoint`, `test_ai_verification_race_condition_postgres`, `auth_status`, `check_mais_schedule_for_user`, `export_to_obsidian`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `FocusService` connect `FocusService` to `utc_now`, `main.py`, `TestFocusCompletion`, `test_ai_verification_race_condition_postgres`, `User`, `focus/routes.py`, `Lesson`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `Lesson` connect `Lesson` to `calculate_diff`, `main.py`, `TestFocusCompletion`, `test_ai_verification_race_condition_postgres`, `FocusService`, `sync/service.py`, `diff.py`, `focus/routes.py`, `User`, `google_calendar/service.py`, `create_test_lesson`, `Database`, `.session`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `FocusService` and `ObsidianPath`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `l()` (e.g. with `Aa()` and `_f()`) actually correct?**
  _`l()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `FocusService` (e.g. with `VerificationResult` and `FocusEvidence`) actually correct?**
  _`FocusService` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `n()` (e.g. with `A()` and `ad()`) actually correct?**
  _`n()` has 44 INFERRED edges - model-reasoned connections that need verification._