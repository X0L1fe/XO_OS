# Graph Report - XO_OS  (2026-09-25)

## Corpus Check
- 74 files · ~92,608 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1115 nodes · 3024 edges · 92 communities (73 shown, 19 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 319 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `96a8a34b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- l
- i
- App.js
- main.py
- parse_ics
- ii
- rd
- telegram/service.py
- Gc
- main.90559390.js
- sync/service.py
- auth/service.py
- post
- hi
- diff.py
- User Guide
- mais_parser.py
- routes.py
- dependencies
- FocusService
- Lesson
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
- focus/service.py
- public/manifest.json
- get_credentials_path
- nc
- _f
- User
- Jr
- LessonChange
- scripts
- get_filtered_semester_lessons
- extends
- MAISync
- sf
- dl
- In
- events_endpoint
- nd
- MAISync logo (XO in black rounded rectangle)
- documentation
- README
- li
- al
- df
- MAISync
- hf
- lo
- xo_os
- Gl
- ql
- focus.js

## God Nodes (most connected - your core abstractions)
1. `l()` - 79 edges
2. `User` - 69 edges
3. `n()` - 59 edges
4. `o()` - 57 edges
5. `i()` - 57 edges
6. `ii()` - 50 edges
7. `Lesson` - 41 edges
8. `LessonData` - 32 edges
9. `Database` - 30 edges
10. `FocusService` - 30 edges

## Surprising Connections (you probably didn't know these)
- `get_calendar_service()` --calls--> `get_token_path()`  [EXTRACTED]
  DEL_DATA.py → app/google_calendar/auth.py
- `make_new()` --calls--> `LessonData`  [EXTRACTED]
  tests/test_diff.py → app/ics/parser.py
- `test_lab_multiple_teachers()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `test_lecture_parsing()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `get_calendar_service()` --calls--> `get_credentials_path()`  [EXTRACTED]
  DEL_DATA.py → app/google_calendar/auth.py

## Import Cycles
- None detected.

## Communities (92 total, 19 thin omitted)

### Community 0 - "l"
Cohesion: 0.10
Nodes (56): A(), An(), ao(), as(), bs(), co(), cs(), Dn() (+48 more)

### Community 1 - "i"
Cohesion: 0.12
Nodes (41): Bt(), ct(), dt(), ef(), fd(), forEach(), Gd(), Ge() (+33 more)

### Community 2 - "App.js"
Cohesion: 0.13
Nodes (9): Achievements(), CalendarObsidianBlock(), Header(), Login(), NextEvent(), Onboarding(), PlayerCard(), RecentChanges() (+1 more)

### Community 3 - "main.py"
Cohesion: 0.06
Nodes (51): get_token_path(), Returns the path to the Google OAuth2 token file., auth_status(), get_achievements(), get_calendar_status(), get_gamification(), get_google_calendars(), get_notifications() (+43 more)

### Community 4 - "parse_ics"
Cohesion: 0.11
Nodes (28): _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), Any, datetime (+20 more)

### Community 5 - "ii"
Cohesion: 0.08
Nodes (37): Aa(), bl(), Bo(), Do(), ei(), El(), Fa(), Go() (+29 more)

### Community 6 - "rd"
Cohesion: 0.12
Nodes (40): ad(), ae(), b(), d(), ee(), et(), fl(), fr() (+32 more)

### Community 7 - "telegram/service.py"
Cohesion: 0.12
Nodes (29): TelegramLinkCode, error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files). (+21 more)

### Community 8 - "Gc"
Cohesion: 0.11
Nodes (39): au(), C(), cu(), du(), _e(), eu(), fu(), Gc() (+31 more)

### Community 9 - "main.90559390.js"
Cohesion: 0.06
Nodes (13): Cr(), Hl(), Kn(), oo(), ps(), Qn(), qs(), remove() (+5 more)

### Community 10 - "sync/service.py"
Cohesion: 0.28
Nodes (9): _apply_lesson_data(), _create_lesson(), datetime, # IMPORTANT:, Update user statistics and gamification data. Awards XP for imported lessons,…, Import a list of LessonData objects (parsed from MAIS schedule or other…, Обновляет существующую БД-запись данными из ICS., SyncResult (+1 more)

### Community 11 - "auth/service.py"
Cohesion: 0.10
Nodes (31): authenticate_user(), confirm_email_change(), create_session(), create_user(), delete_session(), get_password_hash(), initiate_email_change(), initiate_password_reset() (+23 more)

### Community 12 - "post"
Cohesion: 0.13
Nodes (21): complete_onboarding(), confirm_email_change_endpoint(), echo(), initiate_email_change_endpoint(), initiate_password_reset_endpoint(), login(), BackgroundTasks, post (+13 more)

### Community 13 - "hi"
Cohesion: 0.09
Nodes (29): af(), ba(), bd(), ca(), ci(), clear(), da(), dd() (+21 more)

### Community 14 - "diff.py"
Cohesion: 0.36
Nodes (10): _as_local(), _date_distance_days(), _find_best_match(), _lesson_score(), datetime, Оценивает вероятность того, что old и new — одно и то же занятие после…, Ищет лучшее fuzzy-сопоставление. Ограничиваем поиск 14 днями, чтобы не…, Приводит datetime к Europe/Moscow. SQLite может вернуть datetime без tzinfo… (+2 more)

### Community 15 - "User Guide"
Cohesion: 0.09
Nodes (21): API Description, Architecture Overview, CLI Commands, Conflict Resolution, Dependencies, Environment Variables, License, Main Components (+13 more)

### Community 16 - "mais_parser.py"
Cohesion: 0.09
Nodes (24): check_mais_schedule_for_user(), get_mais_groups(), import_mais_schedule(), periodic_mais_check(), Get list of MAIS groups., Import schedule for a given MAIS group name., Check for schedule changes for a specific user and create notifications if…, Background task that periodically checks for MAIS schedule changes for all… (+16 more)

### Community 17 - "routes.py"
Cohesion: 0.14
Nodes (22): get_ai_verification_service(), add_evidence_to_focus_session(), _calculate_elapsed_seconds(), complete_focus_session(), get_active_focus_session(), get_focus_session(), pause_focus_session(), _process_ai_verification() (+14 more)

### Community 18 - "dependencies"
Cohesion: 0.10
Nodes (21): axios, react, react-dom, react-icons, react-router-dom, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+13 more)

### Community 19 - "FocusService"
Cohesion: 0.14
Nodes (14): FocusEvidence, FocusSession, publish_focus_updated(), Publish a focus session updated event to all connections for a user., FocusService, Resume a paused focus session., Complete a focus session. If completion_mode is "manual", we award base XP and…, Get the active focus session for the user, if any. (+6 more)

### Community 20 - "Lesson"
Cohesion: 0.15
Nodes (15): Base, Lesson, get_google_calendar_service(), Authenticates with Google Calendar API and returns a service object. Handles…, _event_to_lesson_key(), GoogleCalendarSyncService, _lesson_to_google_event(), datetime (+7 more)

### Community 21 - "StatsSection.js"
Cohesion: 0.17
Nodes (7): formatNumber(), PlanFact(), StatsSection(), formatNumber(), TopSubjects(), formatNumber(), WeeklyChart()

### Community 22 - "normalize_schedule_category"
Cohesion: 0.11
Nodes (23): get_now(), get_schedule(), get_schedule_exclusions(), get_schedule_filters(), lesson_is_excluded_by_category(), lesson_is_excluded_by_subject(), lesson_is_visible(), normalize_schedule_category() (+15 more)

### Community 23 - "LlamaCppClient"
Cohesion: 0.15
Nodes (10): get_llama_client(), LlamaCppClient, Any, Send a chat completion request to the llama.cpp server., AIVerificationService, Any, Verify the evidence against the goal using the AI model., Build a prompt for the AI to verify evidence against the goal. We ask for a… (+2 more)

### Community 24 - "LessonData"
Cohesion: 0.14
Nodes (19): UserStats, LessonData, Нормализованное занятие MAISync. source_uid: Оригинальный UID из ICS. Сохраняем…, Совместимость с предыдущей версией проекта. В будущем лучше везде перейти на…, Хэш всех изменяемых данных занятия. Если хэш поменялся — занятие необходимо…, DiffResult, _apply_lesson_data(), _create_lesson() (+11 more)

### Community 25 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 26 - "Database"
Cohesion: 0.15
Nodes (17): build_parser(), cmd_export(), cmd_import_ics(), cmd_stats(), cmd_status(), main(), Export lessons to Obsidian., Show user statistics. (+9 more)

### Community 28 - "bu"
Cohesion: 0.17
Nodes (20): ar(), Be(), bu(), cc(), dc(), Er(), fc(), gu() (+12 more)

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
Cohesion: 0.18
Nodes (19): AuthStatusResponse, Config, BaseModel, TokenResponse, UserBase, UserCreate, UserLogin, UserResponse (+11 more)

### Community 40 - "devDependencies"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 41 - "development"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 42 - "web/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 44 - "focus/service.py"
Cohesion: 0.14
Nodes (15): XPTransaction, event_publisher(), publish_gamification_updated(), Publish events for a specific user., Publish a gamification updated event to all connections for a user., lesson_is_excluded_by_category(), lesson_is_excluded_by_subject(), lesson_is_visible() (+7 more)

### Community 45 - "public/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 46 - "get_credentials_path"
Cohesion: 0.21
Nodes (12): get_credentials_path(), get_data_dir(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., clear_calendar(), _delete_callback(), get_calendar_service(), get_event_ids_from_db() (+4 more)

### Community 47 - "nc"
Cohesion: 0.33
Nodes (11): ac(), bi(), Cl(), ec(), fi(), ji(), nc(), rc() (+3 more)

### Community 48 - "_f"
Cohesion: 0.20
Nodes (8): constructor(), _f(), ha(), Je(), qf(), Ue(), xf(), zl

### Community 49 - "User"
Cohesion: 0.12
Nodes (19): get_current_active_user(), get_current_user(), get_user_from_session(), User, export_to_obsidian(), get_current_user_info(), logout(), mark_notification_as_read() (+11 more)

### Community 51 - "LessonChange"
Cohesion: 0.20
Nodes (5): LessonChange, Результат сравнения одного занятия. kind: CREATED UPDATED MOVED DELETED…, Человекочитаемое описание изменения., GoogleCalendarServiceProtocol, Protocol

### Community 52 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 53 - "get_filtered_semester_lessons"
Cohesion: 0.15
Nodes (19): _as_aware_utc(), clipped_lesson_duration_hours(), get_filtered_semester_lessons(), get_plan_fact(), get_semester_bounds(), get_semester_stats(), get_top_subjects(), get_weekly_stats() (+11 more)

### Community 54 - "extends"
Cohesion: 0.50
Nodes (4): react-app, react-app/jest, eslintConfig, extends

### Community 56 - "sf"
Cohesion: 0.27
Nodes (10): bf(), De(), Dr(), Me(), sf(), tu(), vf(), wf() (+2 more)

### Community 65 - "In"
Cohesion: 0.29
Nodes (7): Gn(), In(), Jn(), Un(), Xl(), yn(), Zn()

### Community 66 - "events_endpoint"
Cohesion: 0.50
Nodes (4): event_publisher(), events_endpoint(), Server-Sent Events endpoint for real-time updates., Publish events for a specific user.

### Community 70 - "nd"
Cohesion: 0.50
Nodes (4): nd(), Of(), td(), Zu()

### Community 74 - "li"
Cohesion: 0.67
Nodes (3): ai(), li(), ri()

### Community 75 - "al"
Cohesion: 0.67
Nodes (3): al(), At(), il()

### Community 76 - "df"
Cohesion: 0.67
Nodes (3): cf(), df(), ff()

### Community 78 - "hf"
Cohesion: 1.00
Nodes (3): hf(), If(), Uf()

## Knowledge Gaps
- **90 isolated node(s):** `Config`, `short_name`, `name`, `icons`, `start_url` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `events_endpoint`, `main.py`, `ObsidianPath`, `telegram/service.py`, `sync/service.py`, `auth/service.py`, `focus/service.py`, `post`, `mais_parser.py`, `routes.py`, `FocusService`, `Lesson`, `get_filtered_semester_lessons`, `normalize_schedule_category`, `LessonChange`, `LessonData`, `Database`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `Lesson` connect `Lesson` to `calculate_diff`, `main.py`, `ObsidianPath`, `sync/service.py`, `focus/service.py`, `diff.py`, `FocusService`, `LessonChange`, `get_filtered_semester_lessons`, `normalize_schedule_category`, `LessonData`, `Database`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `SyncService` connect `Database` to `main.py`, `sync/service.py`, `mais_parser.py`, `User`, `LessonChange`, `Lesson`, `LessonData`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `l()` (e.g. with `H()` and `hf()`) actually correct?**
  _`l()` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `User` (e.g. with `FocusService` and `ObsidianPath`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `n()` (e.g. with `A()` and `ad()`) actually correct?**
  _`n()` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `o()` (e.g. with `bu()` and `cs()`) actually correct?**
  _`o()` has 22 INFERRED edges - model-reasoned connections that need verification._