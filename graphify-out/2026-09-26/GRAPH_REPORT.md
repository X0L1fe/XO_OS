# Graph Report - XO_OS  (2026-09-26)

## Corpus Check
- 79 files · ~94,770 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1173 nodes · 3151 edges · 93 communities (73 shown, 20 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 324 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2e0c8f19`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- l
- i
- App.js
- main.py
- parse_ics
- ii
- n
- telegram/service.py
- Gc
- main.90559390.js
- sync/service.py
- ._render_template
- post
- hi
- diff.py
- User Guide
- mais_parser.py
- User
- dependencies
- FocusService
- google_calendar/service.py
- StatsSection.js
- normalize_schedule_category
- LlamaCppClient
- LessonData
- Learn More
- Database
- Settings.js
- bu
- EmailChangePage.jsx
- ScheduleList.js
- NowBlock.js
- calculate_diff
- DonutChart.js
- PasswordResetPage.jsx
- index.js
- Sidebar
- package.json
- ObsidianPath
- web/index.html
- devDependencies
- development
- web/manifest.json
- react-scripts
- Lesson
- public/manifest.json
- get_token_path
- nc
- Zo
- export_to_obsidian
- Jr
- stats/routes.py
- scripts
- stats/service.py
- extends
- MAISync
- Kc
- dl
- In
- telegram_link
- nd
- MAISync logo (XO in black rounded rectangle)
- documentation
- README
- yi
- Текущая архитектура (монолит)
- periodic_mais_check
- MAISync
- hf
- rr
- xo_os
- Gl
- architecture-target.md
- focus.js
- service-boundaries.md

## God Nodes (most connected - your core abstractions)
1. `l()` - 79 edges
2. `User` - 77 edges
3. `n()` - 59 edges
4. `o()` - 57 edges
5. `i()` - 57 edges
6. `Lesson` - 51 edges
7. `ii()` - 50 edges
8. `LessonData` - 32 edges
9. `Database` - 30 edges
10. `FocusService` - 30 edges

## Surprising Connections (you probably didn't know these)
- `make_new()` --calls--> `LessonData`  [EXTRACTED]
  tests/test_diff.py → app/ics/parser.py
- `test_lab_multiple_teachers()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `test_lecture_parsing()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `get_calendar_service()` --calls--> `get_credentials_path()`  [EXTRACTED]
  DEL_DATA.py → app/google_calendar/auth.py
- `get_calendar_service()` --calls--> `get_token_path()`  [EXTRACTED]
  DEL_DATA.py → app/google_calendar/auth.py

## Import Cycles
- None detected.

## Communities (93 total, 20 thin omitted)

### Community 0 - "l"
Cohesion: 0.13
Nodes (41): al(), An(), ao(), as(), At(), bs(), cs(), Dn() (+33 more)

### Community 1 - "i"
Cohesion: 0.11
Nodes (45): ba(), Bt(), ct(), dd(), dt(), fd(), forEach(), Gd() (+37 more)

### Community 2 - "App.js"
Cohesion: 0.13
Nodes (9): Achievements(), CalendarObsidianBlock(), Header(), Login(), NextEvent(), Onboarding(), PlayerCard(), RecentChanges() (+1 more)

### Community 3 - "main.py"
Cohesion: 0.05
Nodes (62): _as_aware_utc(), auth_status(), clipped_lesson_duration_hours(), event_publisher(), events_endpoint(), get_achievements(), get_calendar_status(), get_filtered_semester_lessons() (+54 more)

### Community 4 - "parse_ics"
Cohesion: 0.11
Nodes (28): _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), Any, datetime (+20 more)

### Community 5 - "ii"
Cohesion: 0.09
Nodes (47): Aa(), bl(), Bo(), co(), d(), Do(), El(), Fa() (+39 more)

### Community 6 - "n"
Cohesion: 0.11
Nodes (49): A(), ad(), ae(), b(), C(), du(), _e(), ee() (+41 more)

### Community 7 - "telegram/service.py"
Cohesion: 0.12
Nodes (29): TelegramLinkCode, error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files). (+21 more)

### Community 8 - "Gc"
Cohesion: 0.09
Nodes (33): af(), au(), ca(), cf(), cu(), da(), df(), eu() (+25 more)

### Community 9 - "main.90559390.js"
Cohesion: 0.06
Nodes (17): ai(), componentDidCatch(), Cr(), Hl(), Kn(), li(), lo(), oo() (+9 more)

### Community 10 - "sync/service.py"
Cohesion: 0.28
Nodes (9): _apply_lesson_data(), _create_lesson(), datetime, # IMPORTANT:, Update user statistics and gamification data. Awards XP for imported lessons,…, Import a list of LessonData objects (parsed from MAIS schedule or other…, Обновляет существующую БД-запись данными из ICS., SyncResult (+1 more)

### Community 11 - "._render_template"
Cohesion: 0.20
Nodes (5): Отправьте электронное письмо для сброса пароля. Args: email: адрес электронной…, Отправьте электронное письмо с запросом подтверждения смены email. Args: email:…, Отправьте электронное письмо с подтверждением новой электронной почты. Args:…, Render a Jinja2 template with the given context. Args: template_name: Name of…, Отправьте электронное письмо с подтверждением регистрации. Args: email: адрес…

### Community 12 - "post"
Cohesion: 0.07
Nodes (39): create_session(), Settings, EmailService, Сервис для отправки писем по SMTP., complete_onboarding(), confirm_email_change_endpoint(), echo(), google_disconnect() (+31 more)

### Community 13 - "hi"
Cohesion: 0.20
Nodes (10): bd(), ci(), di(), hi(), ja(), lu(), mi(), pi() (+2 more)

### Community 14 - "diff.py"
Cohesion: 0.36
Nodes (10): _as_local(), _date_distance_days(), _find_best_match(), _lesson_score(), datetime, Оценивает вероятность того, что old и new — одно и то же занятие после…, Ищет лучшее fuzzy-сопоставление. Ограничиваем поиск 14 днями, чтобы не…, Приводит datetime к Europe/Moscow. SQLite может вернуть datetime без tzinfo… (+2 more)

### Community 15 - "User Guide"
Cohesion: 0.09
Nodes (21): API Description, Architecture Overview, CLI Commands, Conflict Resolution, Dependencies, Environment Variables, License, Main Components (+13 more)

### Community 16 - "mais_parser.py"
Cohesion: 0.14
Nodes (16): check_mais_schedule_for_user(), import_mais_schedule(), Import schedule for a given MAIS group name., Check for schedule changes for a specific user and create notifications if…, async_fetch_group_schedule(), async_fetch_groups(), fetch_group_schedule(), _parse_date() (+8 more)

### Community 17 - "User"
Cohesion: 0.10
Nodes (40): authenticate_user(), confirm_email_change(), create_user(), delete_session(), get_current_active_user(), get_current_user(), get_password_hash(), get_user_from_session() (+32 more)

### Community 18 - "dependencies"
Cohesion: 0.10
Nodes (21): axios, react, react-dom, react-icons, react-router-dom, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+13 more)

### Community 19 - "FocusService"
Cohesion: 0.10
Nodes (28): Base, FocusEvidence, FocusSession, Исключение из отображения расписания пользователя. exclusion_type: - "category"…, ScheduleExclusion, UserStats, XPTransaction, event_publisher() (+20 more)

### Community 20 - "google_calendar/service.py"
Cohesion: 0.17
Nodes (12): get_google_calendar_service(), Authenticates with Google Calendar API and returns a service object. Handles…, _event_to_lesson_key(), GoogleCalendarSyncService, _lesson_to_google_event(), datetime, Получает события из целевого календаря Google Calendar. Возвращает список…, Обнаруживает события в Google Calendar, у которых нет соответствующего… (+4 more)

### Community 21 - "StatsSection.js"
Cohesion: 0.17
Nodes (7): formatNumber(), PlanFact(), StatsSection(), formatNumber(), TopSubjects(), formatNumber(), WeeklyChart()

### Community 22 - "normalize_schedule_category"
Cohesion: 0.11
Nodes (21): get_now(), get_schedule_exclusions(), lesson_is_excluded_by_category(), lesson_is_excluded_by_subject(), lesson_is_visible(), normalize_schedule_category(), Полностью заменяет набор исключений текущего пользователя. Пример: {…, Normalize lesson category. Unknown categories are preserved as-is. (+13 more)

### Community 23 - "LlamaCppClient"
Cohesion: 0.14
Nodes (11): get_llama_client(), LlamaCppClient, Any, Send a chat completion request to the llama.cpp server., AIVerificationService, get_ai_verification_service(), Any, Verify the evidence against the goal using the AI model. (+3 more)

### Community 24 - "LessonData"
Cohesion: 0.10
Nodes (23): LessonData, Нормализованное занятие MAISync. source_uid: Оригинальный UID из ICS. Сохраняем…, Совместимость с предыдущей версией проекта. В будущем лучше везде перейти на…, Хэш всех изменяемых данных занятия. Если хэш поменялся — занятие необходимо…, DiffResult, LessonChange, Результат сравнения одного занятия. kind: CREATED UPDATED MOVED DELETED…, Человекочитаемое описание изменения. (+15 more)

### Community 25 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 26 - "Database"
Cohesion: 0.15
Nodes (17): build_parser(), cmd_export(), cmd_import_ics(), cmd_stats(), cmd_status(), main(), Export lessons to Obsidian., Show user statistics. (+9 more)

### Community 28 - "bu"
Cohesion: 0.32
Nodes (12): ar(), Be(), bu(), Er(), gu(), ju(), ku(), lr() (+4 more)

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

### Community 38 - "ObsidianPath"
Cohesion: 0.23
Nodes (15): AuthStatusResponse, Config, BaseModel, TokenResponse, UserBase, UserCreate, UserLogin, UserResponse (+7 more)

### Community 40 - "devDependencies"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 41 - "development"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 42 - "web/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 44 - "Lesson"
Cohesion: 0.28
Nodes (9): Lesson, lesson_is_excluded_by_category(), lesson_is_excluded_by_subject(), lesson_is_visible(), normalize_schedule_category(), Normalize schedule category for comparison., Check if a lesson should be visible based on user's exclusions., Check if lesson is excluded by category. (+1 more)

### Community 45 - "public/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 46 - "get_token_path"
Cohesion: 0.15
Nodes (18): get_credentials_path(), get_data_dir(), get_token_path(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., Returns the path to the Google OAuth2 token file., google_auth(), google_callback() (+10 more)

### Community 47 - "nc"
Cohesion: 0.33
Nodes (11): ac(), bi(), Cl(), ec(), fi(), ji(), nc(), rc() (+3 more)

### Community 48 - "Zo"
Cohesion: 0.13
Nodes (15): constructor(), De(), ei(), ga(), Go(), ha(), ho(), Jo() (+7 more)

### Community 49 - "export_to_obsidian"
Cohesion: 0.29
Nodes (7): export_to_obsidian(), get_current_user_info(), logout(), Any, Экспортируйте занятия в Obsidian., Log out the current user., Get the current user.

### Community 51 - "stats/routes.py"
Cohesion: 0.12
Nodes (30): _as_aware_utc(), clipped_lesson_duration_hours(), get_filtered_semester_lessons(), get_plan_fact(), get_schedule_exclusions(), get_semester_bounds(), get_semester_stats(), get_stats() (+22 more)

### Community 52 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 53 - "stats/service.py"
Cohesion: 0.15
Nodes (20): Session, _as_aware_utc(), clipped_lesson_duration_hours(), get_filtered_semester_lessons(), get_schedule_exclusions(), get_semester_bounds(), lesson_duration_hours(), lesson_is_visible() (+12 more)

### Community 54 - "extends"
Cohesion: 0.50
Nodes (4): react-app, react-app/jest, eslintConfig, extends

### Community 56 - "Kc"
Cohesion: 0.13
Nodes (23): bf(), Dr(), ef(), _f(), Fe(), gf(), io(), Je() (+15 more)

### Community 65 - "In"
Cohesion: 0.29
Nodes (7): Gn(), In(), Jn(), Un(), Xl(), yn(), Zn()

### Community 66 - "telegram_link"
Cohesion: 0.22
Nodes (10): Создаёт одноразовый код привязки учетной записи Telegram и создаёт Telegram…, Return Telegram connection status., Unlink Telegram account., telegram_link(), telegram_status(), telegram_unlink(), BaseModel, TelegramLinkResponse (+2 more)

### Community 70 - "nd"
Cohesion: 0.50
Nodes (4): nd(), Of(), td(), Zu()

### Community 74 - "yi"
Cohesion: 0.60
Nodes (6): cc(), dc(), fc(), ic(), uc(), yi()

### Community 75 - "Текущая архитектура (монолит)"
Cohesion: 0.40
Nodes (4): Внешние зависимости, Основной файл: app/main.py, Структура пакетов, Текущая архитектура (монолит)

### Community 76 - "periodic_mais_check"
Cohesion: 0.50
Nodes (4): periodic_mais_check(), Background task that periodically checks for MAIS schedule changes for all…, start_background_tasks(), on_event

### Community 78 - "hf"
Cohesion: 0.24
Nodes (9): clear(), eject(), hf(), If(), mf(), tu(), Uf(), use() (+1 more)

## Knowledge Gaps
- **95 isolated node(s):** `Config`, `short_name`, `name`, `icons`, `start_url` (+90 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `telegram_link`, `main.py`, `ObsidianPath`, `telegram/service.py`, `sync/service.py`, `post`, `mais_parser.py`, `export_to_obsidian`, `FocusService`, `stats/routes.py`, `stats/service.py`, `normalize_schedule_category`, `LessonData`, `Database`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `Lesson` connect `Lesson` to `calculate_diff`, `main.py`, `ObsidianPath`, `sync/service.py`, `diff.py`, `FocusService`, `google_calendar/service.py`, `stats/routes.py`, `normalize_schedule_category`, `stats/service.py`, `LessonData`, `Database`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `main.py`, `ObsidianPath`, `telegram/service.py`, `sync/service.py`, `User`, `FocusService`, `google_calendar/service.py`, `LessonData`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `l()` (e.g. with `H()` and `hf()`) actually correct?**
  _`l()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `User` (e.g. with `FocusService` and `ObsidianPath`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `n()` (e.g. with `A()` and `ad()`) actually correct?**
  _`n()` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `o()` (e.g. with `bu()` and `cs()`) actually correct?**
  _`o()` has 22 INFERRED edges - model-reasoned connections that need verification._