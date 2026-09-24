# Graph Report - XO_OS  (2026-09-24)

## Corpus Check
- 67 files · ~83,681 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 974 nodes · 2668 edges · 73 communities (59 shown, 14 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 275 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8a56548c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- n
- main.3690f54d.js
- App.js
- main.py
- parse_ics
- Yr
- xi
- telegram/service.py
- ii
- l
- Lesson
- auth/service.py
- post
- so
- LessonData
- User Guide
- mais_parser.py
- Yc
- dependencies
- EmailService
- google_calendar/service.py
- StatsSection.js
- normalize_schedule_category
- al
- User
- Learn More
- Database
- Settings.js
- fl
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
- public/manifest.json
- export_to_obsidian
- scripts
- get_filtered_semester_lessons
- extends
- MAISync
- MAISync logo (XO in black rounded rectangle)
- documentation
- README
- MAISync
- xo_os

## God Nodes (most connected - your core abstractions)
1. `l()` - 84 edges
2. `n()` - 62 edges
3. `i()` - 57 edges
4. `s()` - 54 edges
5. `User` - 51 edges
6. `ii()` - 46 edges
7. `so()` - 32 edges
8. `u()` - 28 edges
9. `Lesson` - 27 edges
10. `rd()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `get_calendar_service()` --calls--> `get_token_path()`  [EXTRACTED]
  DEL_DATA.py → app/google_calendar/auth.py
- `make_new()` --calls--> `LessonData`  [EXTRACTED]
  tests/test_diff.py → app/ics/parser.py
- `test_lab_multiple_teachers()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `test_lecture_parsing()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `test_create_update_and_delete()` --calls--> `SyncService`  [EXTRACTED]
  tests/test_sync.py → app/sync/service.py

## Import Cycles
- None detected.

## Communities (73 total, 14 thin omitted)

### Community 0 - "n"
Cohesion: 0.06
Nodes (110): ad(), ae(), b(), Be(), bf(), bt(), C(), ca() (+102 more)

### Community 1 - "main.3690f54d.js"
Cohesion: 0.05
Nodes (51): ai(), At(), ba(), bd(), cf(), ci(), clear(), dd() (+43 more)

### Community 2 - "App.js"
Cohesion: 0.13
Nodes (9): Achievements(), CalendarObsidianBlock(), Header(), Login(), NextEvent(), Onboarding(), PlayerCard(), RecentChanges() (+1 more)

### Community 3 - "main.py"
Cohesion: 0.08
Nodes (41): get_user_from_session(), get_token_path(), Returns the path to the Google OAuth2 token file., get_calendar_status(), get_current_active_user(), get_current_user(), get_google_calendars(), get_mais_groups() (+33 more)

### Community 4 - "parse_ics"
Cohesion: 0.11
Nodes (28): _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), Any, datetime (+20 more)

### Community 5 - "Yr"
Cohesion: 0.08
Nodes (20): Aa(), af(), Br(), ea(), eject(), Hr(), Ir(), Kr() (+12 more)

### Community 6 - "xi"
Cohesion: 0.09
Nodes (37): ac(), ar(), bi(), bu(), cc(), dc(), ec(), fc() (+29 more)

### Community 7 - "telegram/service.py"
Cohesion: 0.12
Nodes (29): TelegramLinkCode, error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files). (+21 more)

### Community 8 - "ii"
Cohesion: 0.11
Nodes (33): bl(), Bs(), De(), ei(), El(), eu(), ga(), Gc() (+25 more)

### Community 9 - "l"
Cohesion: 0.15
Nodes (32): ao(), bo(), Cl(), co(), eo(), fo(), go(), ho() (+24 more)

### Community 10 - "Lesson"
Cohesion: 0.14
Nodes (18): Lesson, DiffResult, LessonChange, Результат сравнения одного занятия. kind: CREATED UPDATED MOVED DELETED…, Человекочитаемое описание изменения., _apply_lesson_data(), _create_lesson(), GoogleCalendarServiceProtocol (+10 more)

### Community 11 - "auth/service.py"
Cohesion: 0.18
Nodes (22): UserLogin, authenticate_user(), confirm_email_change(), create_session(), create_user(), delete_session(), get_password_hash(), initiate_email_change() (+14 more)

### Community 12 - "post"
Cohesion: 0.09
Nodes (27): complete_onboarding(), confirm_email_change_endpoint(), echo(), google_callback(), initiate_email_change_endpoint(), initiate_password_reset_endpoint(), mark_notification_as_read(), Set the MAIS group for the current user. (+19 more)

### Community 13 - "so"
Cohesion: 0.13
Nodes (21): A(), as(), componentDidCatch(), constructor(), ds(), en(), Fe(), fs() (+13 more)

### Community 14 - "LessonData"
Cohesion: 0.21
Nodes (14): LessonData, Нормализованное занятие MAISync. source_uid: Оригинальный UID из ICS. Сохраняем…, Совместимость с предыдущей версией проекта. В будущем лучше везде перейти на…, Хэш всех изменяемых данных занятия. Если хэш поменялся — занятие необходимо…, _as_local(), _date_distance_days(), _find_best_match(), _lesson_score() (+6 more)

### Community 15 - "User Guide"
Cohesion: 0.09
Nodes (21): API Description, Architecture Overview, CLI Commands, Conflict Resolution, Dependencies, Environment Variables, License, Main Components (+13 more)

### Community 16 - "mais_parser.py"
Cohesion: 0.15
Nodes (14): import_mais_schedule(), Import schedule for a given MAIS group name., async_fetch_group_schedule(), async_fetch_groups(), fetch_group_schedule(), _parse_date(), parse_mais_schedule(), _parse_time() (+6 more)

### Community 17 - "Yc"
Cohesion: 0.19
Nodes (19): au(), cu(), Dr(), du(), fu(), hu(), io(), mu() (+11 more)

### Community 18 - "dependencies"
Cohesion: 0.10
Nodes (21): axios, react, react-dom, react-icons, react-router-dom, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+13 more)

### Community 19 - "EmailService"
Cohesion: 0.18
Nodes (8): Settings, EmailService, Отправьте электронное письмо для сброса пароля. Args: email: адрес электронной…, Сервис для отправки писем по SMTP., Отправьте электронное письмо с запросом подтверждения смены email. Args: email:…, Отправьте электронное письмо с подтверждением новой электронной почты. Args:…, Render a Jinja2 template with the given context. Args: template_name: Name of…, Отправьте электронное письмо с подтверждением регистрации. Args: email: адрес…

### Community 20 - "google_calendar/service.py"
Cohesion: 0.09
Nodes (23): get_credentials_path(), get_data_dir(), get_google_calendar_service(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., Authenticates with Google Calendar API and returns a service object. Handles…, _event_to_lesson_key(), _lesson_to_google_event() (+15 more)

### Community 21 - "StatsSection.js"
Cohesion: 0.17
Nodes (7): formatNumber(), PlanFact(), StatsSection(), formatNumber(), TopSubjects(), formatNumber(), WeeklyChart()

### Community 22 - "normalize_schedule_category"
Cohesion: 0.19
Nodes (14): get_now(), get_schedule(), get_schedule_filters(), lesson_is_visible(), normalize_schedule_category(), normalize_schedule_value(), Возвращает ближайшие занятия текущего пользователя с учётом персональных…, Normalize a schedule value for comparison. Example: " Программирование " ->… (+6 more)

### Community 23 - "al"
Cohesion: 0.17
Nodes (10): al(), An(), bn(), dl(), Gl(), il(), ma(), ql() (+2 more)

### Community 24 - "User"
Cohesion: 0.18
Nodes (20): Base, Notification, Исключение из отображения расписания пользователя. exclusion_type: - "category"…, ScheduleExclusion, Session, User, UserStats, check_mais_schedule_for_user() (+12 more)

### Community 25 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 26 - "Database"
Cohesion: 0.19
Nodes (15): build_parser(), cmd_export(), cmd_import_ics(), cmd_stats(), cmd_status(), main(), Export lessons to Obsidian., Show user statistics. (+7 more)

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
Cohesion: 0.29
Nodes (9): AuthStatusResponse, Config, BaseModel, TokenResponse, UserBase, UserCreate, UserResponse, auth_status() (+1 more)

### Community 40 - "devDependencies"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 41 - "development"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 42 - "web/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 45 - "public/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 49 - "export_to_obsidian"
Cohesion: 0.20
Nodes (10): export_to_obsidian(), get_current_user_info(), get_obsidian_path(), get_obsidian_vault_path(), logout(), Any, Get saved Obsidian vault path., Экспортируйте занятия в Obsidian. (+2 more)

### Community 52 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 53 - "get_filtered_semester_lessons"
Cohesion: 0.11
Nodes (25): _as_aware_utc(), clipped_lesson_duration_hours(), get_filtered_semester_lessons(), get_plan_fact(), get_schedule_exclusions(), get_semester_bounds(), get_semester_stats(), get_top_subjects() (+17 more)

### Community 54 - "extends"
Cohesion: 0.50
Nodes (4): react-app, react-app/jest, eslintConfig, extends

## Knowledge Gaps
- **89 isolated node(s):** `Config`, `short_name`, `name`, `icons`, `start_url` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `main.py`, `auth/schemas.py`, `telegram/service.py`, `Lesson`, `auth/service.py`, `post`, `mais_parser.py`, `export_to_obsidian`, `get_filtered_semester_lessons`, `normalize_schedule_category`, `Database`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `parse_ics()` connect `parse_ics` to `Lesson`, `LessonData`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `main.py`, `telegram/service.py`, `Lesson`, `google_calendar/service.py`, `get_filtered_semester_lessons`, `User`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `l()` (e.g. with `ea()` and `_f()`) actually correct?**
  _`l()` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `n()` (e.g. with `A()` and `ad()`) actually correct?**
  _`n()` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `i()` (e.g. with `A()` and `cu()`) actually correct?**
  _`i()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `s()` (e.g. with `bu()` and `cu()`) actually correct?**
  _`s()` has 21 INFERRED edges - model-reasoned connections that need verification._