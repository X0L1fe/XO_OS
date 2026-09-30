# Graph Report - XO_OS  (2026-09-28)

## Corpus Check
- 93 files · ~94,523 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1151 nodes · 3125 edges · 90 communities (72 shown, 18 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 314 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `69d4a457`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- l
- n
- App.js
- main.py
- parse_ics
- ii
- ml
- telegram/service.py
- Gc
- main.90559390.js
- sync/service.py
- EmailService
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
- gi
- LlamaCppClient
- LessonData
- Learn More
- Database
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
- forEach
- public/manifest.json
- get_token_path
- nc
- pd
- stats-router-extract.md
- Jr
- models.py
- scripts
- Lesson
- extends
- MAISync
- Kc
- dl
- In
- MAISync logo (XO in black rounded rectangle)
- documentation
- README
- nd
- Текущая архитектура (монолит)
- li
- MAISync
- xo_os
- architecture-target.md
- focus.js
- service-boundaries.md

## God Nodes (most connected - your core abstractions)
1. `l()` - 79 edges
2. `User` - 77 edges
3. `n()` - 59 edges
4. `o()` - 57 edges
5. `i()` - 57 edges
6. `ii()` - 50 edges
7. `Lesson` - 42 edges
8. `LessonData` - 32 edges
9. `FocusService` - 30 edges
10. `Database` - 29 edges

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

## Communities (90 total, 18 thin omitted)

### Community 0 - "l"
Cohesion: 0.13
Nodes (33): al(), An(), as(), ds(), es(), fs(), gs(), ha() (+25 more)

### Community 1 - "n"
Cohesion: 0.08
Nodes (75): A(), ad(), b(), ba(), bs(), Bt(), C(), Cr() (+67 more)

### Community 2 - "App.js"
Cohesion: 0.13
Nodes (9): Achievements(), CalendarObsidianBlock(), Header(), Login(), NextEvent(), Onboarding(), PlayerCard(), RecentChanges() (+1 more)

### Community 3 - "main.py"
Cohesion: 0.06
Nodes (52): AuthStatusResponse, auth_status(), event_publisher(), events_endpoint(), export_to_obsidian(), get_achievements(), get_calendar_status(), get_current_user_info() (+44 more)

### Community 4 - "parse_ics"
Cohesion: 0.11
Nodes (28): _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), Any, datetime (+20 more)

### Community 5 - "ii"
Cohesion: 0.08
Nodes (46): Aa(), bl(), Bo(), co(), d(), De(), Do(), ei() (+38 more)

### Community 6 - "ml"
Cohesion: 0.16
Nodes (18): constructor(), Fa(), fl(), H(), J(), K(), ll(), m() (+10 more)

### Community 7 - "telegram/service.py"
Cohesion: 0.12
Nodes (29): TelegramLinkCode, error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files). (+21 more)

### Community 8 - "Gc"
Cohesion: 0.09
Nodes (45): ae(), ar(), At(), au(), Be(), bu(), cf(), cu() (+37 more)

### Community 9 - "main.90559390.js"
Cohesion: 0.08
Nodes (10): componentDidCatch(), Gl(), Kn(), lo(), on(), ql(), Qn(), remove() (+2 more)

### Community 10 - "sync/service.py"
Cohesion: 0.28
Nodes (9): _apply_lesson_data(), _create_lesson(), datetime, # IMPORTANT:, Update user statistics and gamification data. Awards XP for imported lessons,…, Import a list of LessonData objects (parsed from MAIS schedule or other…, Обновляет существующую БД-запись данными из ICS., SyncResult (+1 more)

### Community 11 - "EmailService"
Cohesion: 0.18
Nodes (8): Settings, EmailService, Отправьте электронное письмо для сброса пароля. Args: email: адрес электронной…, Сервис для отправки писем по SMTP., Отправьте электронное письмо с запросом подтверждения смены email. Args: email:…, Отправьте электронное письмо с подтверждением новой электронной почты. Args:…, Render a Jinja2 template with the given context. Args: template_name: Name of…, Отправьте электронное письмо с подтверждением регистрации. Args: email: адрес…

### Community 12 - "post"
Cohesion: 0.08
Nodes (31): complete_onboarding(), confirm_email_change_endpoint(), echo(), google_disconnect(), initiate_email_change_endpoint(), initiate_password_reset_endpoint(), login(), mark_notification_as_read() (+23 more)

### Community 13 - "hi"
Cohesion: 0.17
Nodes (12): bd(), ci(), dd(), hi(), ja(), mi(), pi(), ud() (+4 more)

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
Cohesion: 0.10
Nodes (40): authenticate_user(), confirm_email_change(), create_session(), create_user(), delete_session(), get_current_active_user(), get_current_user(), get_password_hash() (+32 more)

### Community 18 - "dependencies"
Cohesion: 0.10
Nodes (21): axios, react, react-dom, react-icons, react-router-dom, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+13 more)

### Community 19 - "FocusService"
Cohesion: 0.07
Nodes (37): FocusSession, event_publisher(), publish_focus_updated(), publish_gamification_updated(), Publish events for a specific user., Publish a focus session updated event to all connections for a user., Publish a gamification updated event to all connections for a user., add_evidence_to_focus_session() (+29 more)

### Community 20 - "google_calendar/service.py"
Cohesion: 0.19
Nodes (10): _event_to_lesson_key(), GoogleCalendarSyncService, _lesson_to_google_event(), datetime, Получает события из целевого календаря Google Calendar. Возвращает список…, Обнаруживает события в Google Calendar, у которых нет соответствующего…, Синхронизирует изменения (созданные, обновленные, удаленные, перемещенные) в…, Извлекает потенциальный идентификатор урока из события Google Calendar.… (+2 more)

### Community 21 - "StatsSection.js"
Cohesion: 0.17
Nodes (7): formatNumber(), PlanFact(), StatsSection(), formatNumber(), TopSubjects(), formatNumber(), WeeklyChart()

### Community 22 - "gi"
Cohesion: 0.29
Nodes (8): ca(), da(), gi(), Hr(), ki(), pu(), ui(), wi()

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
Cohesion: 0.39
Nodes (7): Config, BaseModel, TokenResponse, UserBase, UserCreate, UserLogin, UserResponse

### Community 40 - "devDependencies"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 41 - "development"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 42 - "web/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 44 - "forEach"
Cohesion: 0.16
Nodes (20): af(), forEach(), Gd(), Jd(), Kd(), lf(), md(), nf() (+12 more)

### Community 45 - "public/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 46 - "get_token_path"
Cohesion: 0.15
Nodes (18): get_credentials_path(), get_data_dir(), get_google_calendar_service(), get_token_path(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., Returns the path to the Google OAuth2 token file., Authenticates with Google Calendar API and returns a service object. Handles… (+10 more)

### Community 47 - "nc"
Cohesion: 0.33
Nodes (11): ac(), bi(), Cl(), ec(), fi(), ji(), nc(), rc() (+3 more)

### Community 48 - "pd"
Cohesion: 0.50
Nodes (4): di(), Ge(), lu(), pd()

### Community 49 - "stats-router-extract.md"
Cohesion: 0.22
Nodes (7): Changes, Files Created, Files Modified, How to Apply, Summary, Verification, Why

### Community 51 - "models.py"
Cohesion: 0.21
Nodes (13): Base, FocusEvidence, Notification, UserStats, XPTransaction, ObsidianPath, BaseModel, Save Obsidian vault path. (+5 more)

### Community 52 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 53 - "Lesson"
Cohesion: 0.07
Nodes (53): get_schedule_exclusions(), lesson_is_excluded_by_category(), lesson_is_excluded_by_subject(), lesson_is_visible(), normalize_schedule_category(), normalize_schedule_value(), Get the user's schedule exclusions as sets of normalized category and subject…, Normalize a schedule value for comparison. Example: " Программирование " ->… (+45 more)

### Community 54 - "extends"
Cohesion: 0.50
Nodes (4): react-app, react-app/jest, eslintConfig, extends

### Community 56 - "Kc"
Cohesion: 0.10
Nodes (31): ao(), bf(), clear(), eject(), eo(), Fe(), fo(), gf() (+23 more)

### Community 65 - "In"
Cohesion: 0.29
Nodes (7): Gn(), In(), Jn(), Un(), Xl(), yn(), Zn()

### Community 74 - "nd"
Cohesion: 0.50
Nodes (4): nd(), Of(), td(), Zu()

### Community 75 - "Текущая архитектура (монолит)"
Cohesion: 0.40
Nodes (4): Внешние зависимости, Основной файл: app/main.py, Структура пакетов, Текущая архитектура (монолит)

### Community 76 - "li"
Cohesion: 0.67
Nodes (3): ai(), li(), ri()

## Knowledge Gaps
- **101 isolated node(s):** `Config`, `short_name`, `name`, `icons`, `start_url` (+96 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `main.py`, `telegram/service.py`, `sync/service.py`, `post`, `mais_parser.py`, `FocusService`, `models.py`, `Lesson`, `LessonData`, `Database`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `Lesson` connect `Lesson` to `calculate_diff`, `main.py`, `sync/service.py`, `diff.py`, `FocusService`, `models.py`, `google_calendar/service.py`, `LessonData`, `Database`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `FocusService` connect `FocusService` to `main.py`, `User`, `models.py`, `Lesson`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `l()` (e.g. with `H()` and `hf()`) actually correct?**
  _`l()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `User` (e.g. with `FocusService` and `ObsidianPath`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `n()` (e.g. with `A()` and `ad()`) actually correct?**
  _`n()` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `o()` (e.g. with `bu()` and `cs()`) actually correct?**
  _`o()` has 22 INFERRED edges - model-reasoned connections that need verification._