# Graph Report - XO_OS  (2026-10-11)

## Corpus Check
- 161 files · ~129,385 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1612 nodes · 4107 edges · 155 communities (116 shown, 39 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 323 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6a404051`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.dc4d312c.js
- l
- App.js
- main.py
- parse_ics
- n
- TestFocusEvidence
- telegram/routes.py
- i
- ii
- _parse_google_date_or_datetime
- forEach
- sync/service.py
- roadmap.md
- FocusService
- User Guide
- mais_parser.py
- auth/service.py
- dependencies
- GoogleCalendarSyncService
- google_calendar/routes.py
- StatsSection.js
- Database
- Session
- Kc
- Learn More
- obsidian/routes.py
- Settings.js
- EmailService
- EmailChangePage.jsx
- ScheduleList.js
- NowBlock.js
- Yc
- hi
- PasswordResetPage.jsx
- .sync_changes
- PlanFact.js
- package.json
- Инженерное решение по переключению Google Calendar в XO_OS
- web/index.html
- devDependencies
- development
- web/manifest.json
- react-scripts
- SyncService
- public/manifest.json
- auth/routes.py
- labels.py
- events_endpoint
- create_test_user
- resend_verification
- focus/service.py
- scripts
- Lesson
- extends
- MAISync
- test_regression_final.py
- WeeklyChart.js
- Settings
- MAISync logo (XO in black rounded rectangle)
- documentation
- README
- get_credentials_path
- Текущая архитектура (монолит)
- get
- MAISync
- db
- FocusSession
- xo_os
- AIVerificationService
- architecture-target.md
- focus.js
- service-boundaries.md
- models.py
- diff.py
- User
- nc
- test_signature_fix.py
- calculate_diff
- test_ai_verification_race_condition_postgres
- logout
- set_custom_colors
- notifications/routes.py
- Итоговое инженерное решение по переключению Google Calendar
- create_test_user
- create_test_focus_session
- Ul
- test_regression_fix.py
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
- .add_evidence
- env.py
- test_boundary.py
- test_boundary_simple.py
- test_pagination_logic.py
- complete_onboarding
- debug_cancel_test.py
- .get_evidence_for_session
- .refresh_colors_for_user
- test_persist_with_better_mock
- test_persist_with_combined_filters
- test_is_all_day_detection
- create_mock_session_with_data
- test_cancellation_isolation_between_calendars
- test_same_google_event_id_two_calendars_isolation
- test_same_google_event_id_two_calendars_isolation
- test_conflict_isolation_between_calendars
- test_user_isolation
- test_imports
- test_fetch_pagination_exists
- test_sync_changes_pagination
- test_imports
- test_method_exists
- test_fetch_exists
- test_sync_changes_exists

## God Nodes (most connected - your core abstractions)
1. `Database` - 129 edges
2. `GoogleCalendarSyncService` - 109 edges
3. `User` - 105 edges
4. `l()` - 71 edges
5. `FocusService` - 63 edges
6. `o()` - 62 edges
7. `i()` - 59 edges
8. `n()` - 55 edges
9. `Lesson` - 53 edges
10. `ii()` - 51 edges

## Surprising Connections (you probably didn't know these)
- `TestFocusCompletionRaceCondition` --uses--> `VerificationResult`  [INFERRED]
  tests/test_focus_race_condition.py → app/ai/verification.py
- `TestFocusCompletion` --uses--> `AIVerificationService`  [INFERRED]
  tests/test_focus_completion.py → app/ai/verification.py
- `TestFocusCompletionRaceCondition` --uses--> `AIVerificationService`  [INFERRED]
  tests/test_focus_race_condition.py → app/ai/verification.py
- `TestFocusCompletion` --uses--> `Database`  [INFERRED]
  tests/test_focus_completion.py → app/database/db.py
- `TestFocusEvidence` --uses--> `Database`  [INFERRED]
  tests/test_focus_evidence.py → app/database/db.py

## Import Cycles
- None detected.

## Communities (155 total, 39 thin omitted)

### Community 0 - "main.dc4d312c.js"
Cohesion: 0.04
Nodes (67): ai(), ar(), At(), Be(), bu(), cc(), cf(), componentDidCatch() (+59 more)

### Community 1 - "l"
Cohesion: 0.12
Nodes (50): An(), ao(), as(), bs(), co(), cs(), d(), Do() (+42 more)

### Community 2 - "App.js"
Cohesion: 0.11
Nodes (11): App(), Achievements(), CalendarObsidianBlock(), Header(), Login(), NextEvent(), Onboarding(), PlayerCard() (+3 more)

### Community 3 - "main.py"
Cohesion: 0.12
Nodes (9): health(), get, echo(), post, Request, get, spa_fallback(), start_background_tasks() (+1 more)

### Community 4 - "parse_ics"
Cohesion: 0.11
Nodes (28): _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), Any, datetime (+20 more)

### Community 5 - "n"
Cohesion: 0.12
Nodes (46): ad(), b(), C(), ca(), dl(), _e(), ee(), es() (+38 more)

### Community 6 - "TestFocusEvidence"
Cohesion: 0.06
Nodes (20): create_test_user(), fixture, Test that valid URL evidence is accepted, Test that valid image evidence is accepted, Helper to create a test user, Test that valid file evidence is accepted, Test that empty evidence content is rejected, Test that whitespace-only evidence content is rejected (+12 more)

### Community 7 - "telegram/routes.py"
Cohesion: 0.08
Nodes (45): TelegramLinkCode, error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files). (+37 more)

### Community 8 - "i"
Cohesion: 0.11
Nodes (43): bt(), Cr(), ct(), dt(), fd(), ft(), Gd(), gt() (+35 more)

### Community 9 - "ii"
Cohesion: 0.08
Nodes (37): A(), Aa(), bl(), Bo(), Br(), da(), ea(), ei() (+29 more)

### Community 10 - "_parse_google_date_or_datetime"
Cohesion: 0.15
Nodes (12): _parse_google_date_or_datetime(), datetime, Фоновая задача для переключения календаря - переносит события уроков из source…, Возвращает True, если событие Google Calendar было создано не ранее момента…, Parses a Google Calendar date or dateTime string into a timezone-aware datetime…, Сохраняет события Google Calendar в локальную базу данных для данного…, Test _persist_google_events with detailed debugging., test_persist_with_detailed_debug() (+4 more)

### Community 11 - "forEach"
Cohesion: 0.11
Nodes (18): af(), clear(), eject(), forEach(), hf(), If(), ja(), ka() (+10 more)

### Community 12 - "sync/service.py"
Cohesion: 0.13
Nodes (19): LessonData, Нормализованное занятие MAISync. source_uid: Оригинальный UID из ICS. Сохраняем…, Совместимость с предыдущей версией проекта. В будущем лучше везде перейти на…, Хэш всех изменяемых данных занятия. Если хэш поменялся — занятие необходимо…, DiffResult, LessonChange, Результат сравнения одного занятия. kind: CREATED UPDATED MOVED DELETED…, Человекочитаемое описание изменения. (+11 more)

### Community 13 - "roadmap.md"
Cohesion: 0.09
Nodes (22): Phase 10 — Real activity streak, Phase 11 — Gamification event architecture, Phase 12 — Auth extraction, Phase 13 — Email extraction, Phase 14 — Telegram extraction, Phase 15 — Sync extraction, Phase 16 — Google Calendar isolation, Phase 17 — MAIS parser isolation (+14 more)

### Community 14 - "FocusService"
Cohesion: 0.17
Nodes (14): VerificationResult, FocusService, Test that manual completion doesn't award XP twice, Test that AI verified completion with score 0.0 awards 10 XP, Test that AI verified completion with score 0.5 awards 15 XP, Test that AI verified completion with score 1.0 awards 20 XP, Test that AI verified completion when rejected awards 0 XP, Test that AI verified completion when error awards 0 XP (+6 more)

### Community 15 - "User Guide"
Cohesion: 0.09
Nodes (21): API Description, Architecture Overview, CLI Commands, Conflict Resolution, Dependencies, Environment Variables, License, Main Components (+13 more)

### Community 16 - "mais_parser.py"
Cohesion: 0.12
Nodes (15): async_fetch_groups(), fetch_group_schedule(), fetch_groups(), _parse_date(), _parse_time(), Fetch the list of groups from MAIS. Returns list of dict with keys: name, fac,…, Fetch schedule JSON for a given group name. Uses MD5 of group name as the…, Fetch the list of groups from MAIS asynchronously. Returns list of dict with… (+7 more)

### Community 17 - "auth/service.py"
Cohesion: 0.16
Nodes (23): authenticate_user(), confirm_email_change(), create_session(), create_user(), get_current_user(), get_password_hash(), get_user_from_session(), initiate_email_change() (+15 more)

### Community 18 - "dependencies"
Cohesion: 0.10
Nodes (21): axios, react, react-dom, react-icons, react-router-dom, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+13 more)

### Community 19 - "GoogleCalendarSyncService"
Cohesion: 0.09
Nodes (22): GoogleCalendarSyncService, Handles cancelled Google Calendar events. For cancelled events…, Test that the connection object is passed correctly., test_connection_passing(), Test _persist_google_events with debug output., test_persist_with_debug(), Test _persist_google_events with proper datetime objects., test_persist_with_proper_datetimes() (+14 more)

### Community 20 - "google_calendar/routes.py"
Cohesion: 0.20
Nodes (14): get_calendar_status(), get, get_data_dir(), get_google_calendar_service(), get_token_path(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 token file., Authenticates with Google Calendar API and returns a service object. Handles… (+6 more)

### Community 21 - "StatsSection.js"
Cohesion: 0.25
Nodes (6): COLORS, DonutChart(), formatNumber(), StatsSection(), formatNumber(), TopSubjects()

### Community 22 - "Database"
Cohesion: 0.08
Nodes (22): Database, Точка входа для фоновой задачи после выбора календаря. Создаёт сервис и…, Test _persist_google_events with correct parameter passing., test_persist_with_correct_params(), Test _persist_google_events with query call tracking., test_persist_with_query_tracking(), Test _persist_google_events with detailed return tracking., test_persist_with_detailed_return_tracking() (+14 more)

### Community 23 - "Session"
Cohesion: 0.12
Nodes (16): Session, get_gamification(), get, post, put, Получите статистику геймификации текущего пользователя (уровень, опыт, серия).…, Обновите настройки геймификации для текущего пользователя. Сюда входят флаг…, Development-only endpoint to reset gamification data for the current user. This… (+8 more)

### Community 24 - "Kc"
Cohesion: 0.17
Nodes (26): ae(), au(), cu(), du(), eu(), fu(), hu(), is() (+18 more)

### Community 25 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 26 - "obsidian/routes.py"
Cohesion: 0.19
Nodes (14): export_to_obsidian(), get_obsidian_path(), get_obsidian_status(), get_obsidian_vault_path(), ObsidianPath, Any, BaseModel, get (+6 more)

### Community 27 - "Settings.js"
Cohesion: 0.20
Nodes (3): COLOR_OPTIONS, CUSTOM_SLOT_KEYS, Settings()

### Community 28 - "EmailService"
Cohesion: 0.21
Nodes (7): EmailService, Отправьте электронное письмо для сброса пароля. Args: email: адрес электронной…, Сервис для отправки писем по SMTP., Отправьте электронное письмо с запросом подтверждения смены email. Args: email:…, Отправьте электронное письмо с подтверждением новой электронной почты. Args:…, Render a Jinja2 template with the given context. Args: template_name: Name of…, Отправьте электронное письмо с подтверждением регистрации. Args: email: адрес…

### Community 30 - "ScheduleList.js"
Cohesion: 0.40
Nodes (3): DEFAULT_CATEGORIES, getPluralForm(), ScheduleList()

### Community 31 - "NowBlock.js"
Cohesion: 0.14
Nodes (9): EMPTY_NOW, FocusState(), formatCurrentTime(), formatElapsedTime(), formatLessonType(), formatVerificationStatus(), LessonState(), NowBlock() (+1 more)

### Community 32 - "Yc"
Cohesion: 0.12
Nodes (19): bf(), constructor(), De(), ef(), _f(), Fe(), gf(), jl() (+11 more)

### Community 33 - "hi"
Cohesion: 0.12
Nodes (18): al(), ba(), bd(), ci(), dd(), ga(), hi(), Hr() (+10 more)

### Community 35 - ".sync_changes"
Cohesion: 0.15
Nodes (8): _lesson_to_google_event(), Преобразует объект Lesson или LessonData в словарь события Google Calendar.…, Получает события из целевого календаря Google Calendar. Возвращает кортеж…, Отправляет локальные изменения (created/updated/moved/deleted) в Google…, Обнаруживает события в Google Calendar, у которых нет соответствующего…, Синхронизирует изменения (созданные, обновленные, удаленные, перемещенные) в…, Синхронизируйте один урок с Календарем Google (создайте или обновите).…, Создаёт события в Google для всех уроков пользователя, у которых…

### Community 36 - "PlanFact.js"
Cohesion: 0.33
Nodes (4): Sidebar(), FiCheck(), formatNumber(), PlanFact()

### Community 37 - "package.json"
Cohesion: 0.20
Nodes (9): author, description, keywords, license, main, name, private, proxy (+1 more)

### Community 38 - "Инженерное решение по переключению Google Calendar в XO_OS"
Cohesion: 0.13
Nodes (14): 1. Рекомендуемая архитектура, 2.1. Добавить новую таблицу для блокировки переключений, 2.2. Расширить GoogleCalendarSyncService методами переключения, 2.3. Обновить маршрут выбора календаря, 2. Необходимые изменения, 3.1. Общий flow, 3.2. Фоновая задача переключения (switch_calendar_for_user), 3.3. Обработание ошибок и восстановление (+6 more)

### Community 40 - "devDependencies"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 41 - "development"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 42 - "web/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 44 - "SyncService"
Cohesion: 0.07
Nodes (32): build_parser(), cmd_export(), cmd_import_ics(), cmd_stats(), cmd_status(), main(), Export lessons to Obsidian., Show user statistics. (+24 more)

### Community 45 - "public/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 46 - "auth/routes.py"
Cohesion: 0.29
Nodes (11): auth_status(), login(), Check authentication status., AuthStatusResponse, Config, BaseModel, TokenResponse, UserBase (+3 more)

### Community 47 - "labels.py"
Cohesion: 0.20
Nodes (12): build_all_labels(), custom_label_name(), custom_label_uuid(), palette_label_uuid(), Определения меток событий Google Calendar. Особенности Google Calendar API: -…, Преобразует значение из lesson_colors в (тип_поля, значение) для Google API.…, Возвращает список меток для передачи в calendars().patch(). custom_colors —…, UUID палитровой метки по её ключу (cocoa, mango, ...). (+4 more)

### Community 48 - "events_endpoint"
Cohesion: 0.33
Nodes (6): event_publisher(), Publish events for a specific user., events_endpoint(), get, Request, Server-Sent Events endpoint for real-time updates.

### Community 49 - "create_test_user"
Cohesion: 0.25
Nodes (8): create_test_user(), db(), fixture, Helper to create a test user, Create a file-based SQLite database for testing, Create a database session, session(), test_user()

### Community 50 - "resend_verification"
Cohesion: 0.22
Nodes (13): confirm_email_change_endpoint(), initiate_email_change_endpoint(), initiate_password_reset_endpoint(), post, Resend verification email to user., Initiate password reset process., Reset password using token and new password., Initiate email change process (requires current authentication). (+5 more)

### Community 51 - "focus/service.py"
Cohesion: 0.23
Nodes (15): Base, FocusEvidence, ScheduleExclusion, UserStats, XPTransaction, publish_gamification_updated(), Publish a gamification updated event to all connections for a user., # TODO: Trigger AI verification in the background (e.g., using a background… (+7 more)

### Community 52 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 53 - "Lesson"
Cohesion: 0.17
Nodes (10): Lesson, create_test_lesson(), Helper to create a test lesson, create_test_lesson(), Test suite for verifying Focus evidence functionality Tests Phase 5 runtime…, Helper to create a test lesson, create_test_lesson(), Helper to create a test lesson (+2 more)

### Community 54 - "extends"
Cohesion: 0.50
Nodes (4): react-app, react-app/jest, eslintConfig, extends

### Community 56 - "test_regression_final.py"
Cohesion: 0.22
Nodes (12): create_mock_session(), Create a mock session that returns empty results for queries., Test that old style call does not throw TypeError., Test that new style call does not throw TypeError., Test that _fetch_google_events is called when google_events is None., Test that _fetch_google_events is NOT called when google_events is provided., Test that sync_changes can be called without TypeError and follows…, test_fetch_called_when_none() (+4 more)

### Community 65 - "Settings"
Cohesion: 0.29
Nodes (5): get_llama_client(), LlamaCppClient, Any, Send a chat completion request to the llama.cpp server. Повторяет запрос при…, Settings

### Community 74 - "get_credentials_path"
Cohesion: 0.27
Nodes (10): get_credentials_path(), Returns the path to the Google OAuth2 client secrets file., clear_calendar(), _delete_callback(), get_calendar_service(), get_event_ids_from_db(), main(), Возвращает авторизованный сервис Google Calendar. (+2 more)

### Community 75 - "Текущая архитектура (монолит)"
Cohesion: 0.40
Nodes (4): Внешние зависимости, Основной файл: app/main.py, Структура пакетов, Текущая архитектура (монолит)

### Community 76 - "get"
Cohesion: 0.18
Nodes (11): get_color_palette(), get_google_calendar_connections(), get_lesson_colors(), google_auth(), google_callback(), get, Handle Google OAuth2 callback., Get the user's Google Calendar connections. (+3 more)

### Community 78 - "db"
Cohesion: 0.67
Nodes (3): db(), fixture, Create a PostgreSQL database for testing

### Community 79 - "FocusSession"
Cohesion: 0.10
Nodes (16): Aware UTC. Для ВСЕЙ логики: фокус-сессии, XP, фоновые задачи, транзакции,…, utc_now(), FocusSession, publish_focus_updated(), Publish a focus session updated event to all connections for a user., Resume a paused focus session., Завершите фокус-сессию. Если для завершения_режима установлено значение…, Наградите пользователя XP и обновите UserStats. Это вызывается, когда… (+8 more)

### Community 81 - "AIVerificationService"
Cohesion: 0.18
Nodes (9): fetch_url_text(), load_image_as_data_url(), Подготовка evidence к отправке в Qwen2.5-VL. Отвечает за: - обрезку текстовых…, Загружает страницу по URL и возвращает очищенный текст. Возвращает None, если…, Читает картинку из MEDIA_ROOT/<rel_path>, ресайзит и возвращает…, truncate_text(), AIVerificationService, Any (+1 more)

### Community 94 - "models.py"
Cohesion: 0.28
Nodes (5): CalendarSwitchLock, GoogleCalendarConnection, GoogleCalendarEvent, _event_to_lesson_key(), Извлекает потенциальный идентификатор урока из события Google Calendar.…

### Community 95 - "diff.py"
Cohesion: 0.36
Nodes (10): _as_local(), _date_distance_days(), _find_best_match(), _lesson_score(), datetime, Оценивает вероятность того, что old и new — одно и то же занятие после…, Ищет лучшее fuzzy-сопоставление. Ограничиваем поиск 14 днями, чтобы не…, Приводит datetime к Europe/Moscow. SQLite может вернуть datetime без tzinfo… (+2 more)

### Community 96 - "User"
Cohesion: 0.05
Nodes (79): get_ai_verification_service(), get_current_active_user(), get_schedule_exclusions(), lesson_is_excluded_by_category(), lesson_is_excluded_by_subject(), lesson_is_visible(), normalize_schedule_category(), normalize_schedule_value() (+71 more)

### Community 97 - "nc"
Cohesion: 0.33
Nodes (11): ac(), bi(), Cl(), ec(), fi(), ji(), nc(), rc() (+3 more)

### Community 98 - "test_signature_fix.py"
Cohesion: 0.18
Nodes (10): Test that sync_changes can be called without TypeError (signature fix)., Test that old style call does not throw TypeError., Test that new style call does not throw TypeError., Test that _fetch_google_events is called when google_events is None., Test that _fetch_google_events is NOT called when google_events is provided., test_fetch_called_when_none(), test_fetch_not_called_when_provided(), test_new_style_call_no_typeerror() (+2 more)

### Community 100 - "calculate_diff"
Cohesion: 0.53
Nodes (9): calculate_diff(), Сравнивает старое состояние с новым. Алгоритм: 1. Exact match по identity_key.…, make_new(), make_old(), test_date_change_is_moved(), test_exact_identity_is_updated(), test_new_lesson_is_created(), test_time_change_is_moved() (+1 more)

### Community 101 - "test_ai_verification_race_condition_postgres"
Cohesion: 0.24
Nodes (10): create_test_focus_session(), create_test_lesson(), create_test_user(), Test that concurrent AI verification processing does not award XP twice using…, Helper to create a test user, Helper to create a test lesson, Helper to create a focus session in the database, Test that concurrent manual completions of the same session do not award XP… (+2 more)

### Community 102 - "logout"
Cohesion: 0.22
Nodes (9): get_current_user_info(), logout(), Any, get, Verify email using token from verification link., Log out the current user., Get the current user., verify_email() (+1 more)

### Community 103 - "set_custom_colors"
Cohesion: 0.28
Nodes (9): google_disconnect(), BackgroundTasks, post, Request, Disconnect/revoke Google OAuth tokens., Сохраняет пользовательские цвета для типов занятий., Сохраняет кастомные цвета (до 6 слотов)., set_custom_colors() (+1 more)

### Community 104 - "notifications/routes.py"
Cohesion: 0.25
Nodes (8): get_notifications(), mark_notification_as_read(), get, post, Get notifications for the current user. Returns a list of notifications sorted…, Mark a notification as read., Toggle notifications enabled for the current user., toggle_notifications_enabled()

### Community 105 - "Итоговое инженерное решение по переключению Google Calendar"
Cohesion: 0.22
Nodes (8): 1. Рекомендуемая архитектура, 2. Необходимые изменения, 3. Пошаговый алгоритм, 4. Таблица восстановления после сбоев, 5. Минимальная матрица тестов, 6. Ограничения и оставшиеся риски, 7. Итоговый вердикт, Итоговое инженерное решение по переключению Google Calendar

### Community 106 - "create_test_user"
Cohesion: 0.25
Nodes (5): create_test_user(), fixture, Helper to create a test user, Create an in-memory SQLite database for testing, Create a database session

### Community 107 - "create_test_focus_session"
Cohesion: 0.25
Nodes (5): create_test_focus_session(), Test that concurrent manual completions of the same session do not award XP…, Test that concurrent AI verification processing does not award XP twice, Test that two focus sessions for the same lesson occurrence cannot both be…, Helper to create a focus session in the database

### Community 109 - "test_regression_fix.py"
Cohesion: 0.29
Nodes (6): Test that _detect_and_handle_conflicts(service) still works., Test that _detect_and_handle_conflicts(service, google_events=...) works., Test that sync_changes can be called without TypeError due to the signature fix., test_new_style_call(), test_old_style_call(), test_sync_changes_flow()

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

### Community 120 - ".add_evidence"
Cohesion: 0.33
Nodes (3): Получите сеанс фокусировки по идентификатору, гарантируя, что он принадлежит…, Проверка и подготовка доказательств к хранению. Возвращает кортеж (тип,…, Add evidence to a focus session.

### Community 121 - "env.py"
Cohesion: 0.40
Nodes (4): Оффлайн-режим: только генерация SQL, без подключения., Онлайн-режим: подключаемся к реальной БД., run_migrations_offline(), run_migrations_online()

### Community 122 - "test_boundary.py"
Cohesion: 0.40
Nodes (4): Test the boundary check function., Test that _persist_google_events respects the boundary., test_is_event_created_after_connection(), test_persist_respects_boundary()

### Community 123 - "test_boundary_simple.py"
Cohesion: 0.40
Nodes (4): Test the boundary check function., Test that _persist_google_events respects the boundary., test_is_event_created_after_connection(), test_persist_respects_boundary()

### Community 124 - "test_pagination_logic.py"
Cohesion: 0.40
Nodes (4): Test that the pagination logic is correctly implemented., Test that the method still works with time_min and time_max parameters., test_backward_compatibility(), test_pagination_logic()

### Community 125 - "complete_onboarding"
Cohesion: 0.50
Nodes (4): complete_onboarding(), post, Request, Complete onboarding by saving group and calendar selection.

## Knowledge Gaps
- **156 isolated node(s):** `Config`, `short_name`, `name`, `icons`, `start_url` (+151 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `TestFocusEvidence`, `telegram/routes.py`, `sync/service.py`, `FocusService`, `auth/service.py`, `GoogleCalendarSyncService`, `google_calendar/routes.py`, `Session`, `obsidian/routes.py`, `SyncService`, `auth/routes.py`, `events_endpoint`, `create_test_user`, `resend_verification`, `focus/service.py`, `Lesson`, `get`, `models.py`, `test_ai_verification_race_condition_postgres`, `logout`, `set_custom_colors`, `notifications/routes.py`, `create_test_user`, `complete_onboarding`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `main.py`, `debug_cancel_test.py`, `TestFocusEvidence`, `telegram/routes.py`, `test_persist_with_better_mock`, `test_persist_with_combined_filters`, `_parse_google_date_or_datetime`, `test_cancellation_isolation_between_calendars`, `sync/service.py`, `test_same_google_event_id_two_calendars_isolation`, `FocusService`, `test_conflict_isolation_between_calendars`, `test_same_google_event_id_two_calendars_isolation`, `test_user_isolation`, `GoogleCalendarSyncService`, `google_calendar/routes.py`, `obsidian/routes.py`, `SyncService`, `auth/routes.py`, `create_test_user`, `resend_verification`, `focus/service.py`, `Lesson`, `test_regression_final.py`, `db`, `models.py`, `User`, `test_signature_fix.py`, `logout`, `create_test_user`, `test_regression_fix.py`, `test_boundary.py`, `test_boundary_simple.py`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `GoogleCalendarSyncService` connect `GoogleCalendarSyncService` to `debug_cancel_test.py`, `.refresh_colors_for_user`, `test_persist_with_better_mock`, `test_persist_with_combined_filters`, `_parse_google_date_or_datetime`, `test_cancellation_isolation_between_calendars`, `sync/service.py`, `test_same_google_event_id_two_calendars_isolation`, `test_conflict_isolation_between_calendars`, `test_same_google_event_id_two_calendars_isolation`, `test_user_isolation`, `google_calendar/routes.py`, `Database`, `.sync_changes`, `SyncService`, `labels.py`, `Lesson`, `test_regression_final.py`, `models.py`, `User`, `test_signature_fix.py`, `test_regression_fix.py`, `test_boundary.py`, `test_boundary_simple.py`, `test_pagination_logic.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `Database` (e.g. with `Base` and `GoogleCalendarSyncService`) actually correct?**
  _`Database` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `GoogleCalendarSyncService` (e.g. with `Database` and `CalendarSwitchLock`) actually correct?**
  _`GoogleCalendarSyncService` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `User` (e.g. with `FocusService` and `GoogleCalendarSyncService`) actually correct?**
  _`User` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `FocusService` (e.g. with `VerificationResult` and `FocusEvidence`) actually correct?**
  _`FocusService` has 8 INFERRED edges - model-reasoned connections that need verification._