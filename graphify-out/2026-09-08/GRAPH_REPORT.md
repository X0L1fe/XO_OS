# Graph Report - MAISync  (2026-09-08)

## Corpus Check
- 64 files · ~104,206 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 791 nodes · 1802 edges · 55 communities (54 shown, 1 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 111 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- LessonData
- a
- main.0833998d.js
- hs
- enterface.md
- ed
- parse_ics
- App.js
- auth/service.py
- User
- User Guide
- Xu
- o
- dependencies
- get_token_path
- mais_parser.py
- main.py
- Learn More
- vc
- H
- ss
- handle_document
- zi
- Решение проблемы дублирования в Telegram боте
- package.json
- devDependencies
- development
- XO_OS Web Version
- web/manifest.json
- qs
- Usage
- public/manifest.json
- UserStats
- Анализ дублирования событий в Google Calendar
- Telegram Bot for XO_OS
- Future Enhancements
- XO_OS
- Статус выполнения задач
- Исправлено дублирование событий в Google Calendar
- scripts
- extends
- migrate.py
- hf

## God Nodes (most connected - your core abstractions)
1. `o()` - 69 edges
2. `ss()` - 41 edges
3. `a()` - 34 edges
4. `hs()` - 30 edges
5. `rf()` - 27 edges
6. `LessonData` - 25 edges
7. `ma()` - 25 edges
8. `User` - 22 edges
9. `Lesson` - 21 edges
10. `es()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `test_lab_multiple_teachers()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `test_lecture_parsing()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `ObsidianPath` --uses--> `UserCreate`  [INFERRED]
  app/main.py → app/auth/schemas.py
- `ObsidianPath` --uses--> `UserLogin`  [INFERRED]
  app/main.py → app/auth/schemas.py
- `ObsidianPath` --uses--> `UserResponse`  [INFERRED]
  app/main.py → app/auth/schemas.py

## Import Cycles
- None detected.

## Communities (55 total, 1 thin omitted)

### Community 0 - "LessonData"
Cohesion: 0.06
Nodes (58): Settings, Database, Lesson, get_google_calendar_service(), Authenticates with Google Calendar API and returns a service object. Handles…, _event_to_lesson_key(), GoogleCalendarSyncService, _lesson_to_google_event() (+50 more)

### Community 1 - "a"
Cohesion: 0.22
Nodes (27): a(), Cd(), d(), es(), f(), g(), Gr(), hd() (+19 more)

### Community 2 - "main.0833998d.js"
Cohesion: 0.06
Nodes (36): ac(), af(), An(), as(), at(), _c(), cs(), da() (+28 more)

### Community 3 - "hs"
Cohesion: 0.13
Nodes (28): B(), bf(), bl(), df(), Do(), ds(), ff(), gs() (+20 more)

### Community 4 - "enterface.md"
Cohesion: 0.06
Nodes (32): 10. Расписание, 11. Следующее событие, 12. Главный статистический блок, 13. Динамика нагрузки, 14. Top Subjects, 15. План против факта, 16. Достижения, 17. Streak (+24 more)

### Community 5 - "ed"
Cohesion: 0.17
Nodes (18): bt(), dd(), ed(), fd(), gf(), iu(), Jf(), Ju() (+10 more)

### Community 6 - "parse_ics"
Cohesion: 0.11
Nodes (28): _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), Any, datetime (+20 more)

### Community 7 - "App.js"
Cohesion: 0.09
Nodes (15): App(), Achievements(), CalendarObsidianBlock(), Header(), NowBlock(), PlayerCard(), ScheduleList(), Settings() (+7 more)

### Community 8 - "auth/service.py"
Cohesion: 0.17
Nodes (20): AuthStatusResponse, Config, BaseModel, TokenResponse, UserBase, UserCreate, UserLogin, UserResponse (+12 more)

### Community 9 - "User"
Cohesion: 0.11
Nodes (23): get_user_from_session(), User, auth_status(), get_current_active_user(), get_current_user(), get_now(), get_obsidian_status(), get_plan_fact() (+15 more)

### Community 10 - "User Guide"
Cohesion: 0.09
Nodes (21): API Description, Architecture Overview, CLI Commands, Conflict Resolution, Dependencies, Environment Variables, License, Main Components (+13 more)

### Community 11 - "Xu"
Cohesion: 0.07
Nodes (42): Ae(), bd(), Bi(), cc(), dc(), De(), _e(), ec() (+34 more)

### Community 12 - "o"
Cohesion: 0.15
Nodes (25): ao(), bo(), co(), Dl(), eo(), fo(), go(), ho() (+17 more)

### Community 13 - "dependencies"
Cohesion: 0.11
Nodes (19): react, react-dom, react-icons, react-scripts, @testing-library/dom, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event (+11 more)

### Community 14 - "get_token_path"
Cohesion: 0.14
Nodes (14): get_credentials_path(), get_data_dir(), get_token_path(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., Returns the path to the Google OAuth2 token file., get_calendar_status(), google_auth() (+6 more)

### Community 15 - "mais_parser.py"
Cohesion: 0.16
Nodes (15): get_mais_groups(), import_mais_schedule(), Get list of MAIS groups., Import schedule for a given MAIS group name., _build_identity_key(), fetch_group_schedule(), fetch_groups(), _parse_date() (+7 more)

### Community 16 - "main.py"
Cohesion: 0.17
Nodes (17): echo(), export_to_obsidian(), get_current_user_info(), get_obsidian_path(), get_obsidian_vault_path(), google_disconnect(), logout(), Any (+9 more)

### Community 17 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 18 - "vc"
Cohesion: 0.24
Nodes (13): ar(), bc(), dr(), Fr(), nr(), or(), rr(), vc() (+5 more)

### Community 19 - "H"
Cohesion: 0.25
Nodes (9): aa(), fa(), H(), ia(), J(), jl(), kf(), la() (+1 more)

### Community 20 - "ss"
Cohesion: 0.07
Nodes (47): ai(), ba(), Br(), Ca(), ci(), cl(), di(), Ea() (+39 more)

### Community 21 - "handle_document"
Cohesion: 0.29
Nodes (9): error_handler(), handle_document(), main(), process_ics_content(), Log errors caused by updates., Handle incoming document messages (expected to be ICS files)., Process ICS content by delegating to the working xo-os import CLI. Optionally…, DEFAULT_TYPE (+1 more)

### Community 22 - "zi"
Cohesion: 0.32
Nodes (8): gc(), hc(), kc(), mc(), ns(), sc(), Xi(), zi()

### Community 23 - "Решение проблемы дублирования в Telegram боте"
Cohesion: 0.20
Nodes (9): Альтернативный подход (если subprocess нежелателен):, Анализ проблемы, Изменения в `app/telegram_bot.py`, Предлагаемое решение, Преимущества этого подхода:, Причина проблемы, Решение проблемы дублирования в Telegram боте, Следующие шаги: (+1 more)

### Community 24 - "package.json"
Cohesion: 0.20
Nodes (9): author, description, keywords, license, main, name, private, proxy (+1 more)

### Community 25 - "devDependencies"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 26 - "development"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 27 - "XO_OS Web Version"
Cohesion: 0.22
Nodes (8): API Endpoints, Dependencies, Development, Notes, Prerequisites, Project Structure, Running the Web Version, XO_OS Web Version

### Community 28 - "web/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 29 - "qs"
Cohesion: 0.16
Nodes (19): ad(), bs(), cu(), du(), eu(), fu(), ks(), lu() (+11 more)

### Community 30 - "Usage"
Cohesion: 0.25
Nodes (7): Changes Made, Current State, Google Calendar Setup, Installation, Running, Usage, XO_OS - Google Calendar Integration Summary

### Community 31 - "public/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 32 - "UserStats"
Cohesion: 0.24
Nodes (10): Base, Session, UserStats, get_achievements(), get_stats(), ObsidianPath, BaseModel, Get stats for the current user. (+2 more)

### Community 33 - "Анализ дублирования событий в Google Calendar"
Cohesion: 0.29
Nodes (6): Анализ дублирования событий в Google Calendar, Как проверить, какой случай у вас есть:, Почему вы всё ещё видите дублирование:, Следующие шаги:, Что можно сделать:, Что я проверил и исправил:

### Community 34 - "Telegram Bot for XO_OS"
Cohesion: 0.29
Nodes (6): Direct URL fetch (optional), Forwarding from external bot, How it works, Setup, Telegram Bot for XO_OS, Usage

### Community 35 - "Future Enhancements"
Cohesion: 0.29
Nodes (6): Documentation, Future Enhancements, Google Calendar, Obsidian Integration, Scheduler, Statistics and Gamification

### Community 36 - "XO_OS"
Cohesion: 0.33
Nodes (5): MVP 0.1, XO_OS, Архитектура, Запуск, Настройка Google Calendar

### Community 37 - "Статус выполнения задач"
Cohesion: 0.33
Nodes (5): Выполнено, Как протестировать, Примечания, Следующие шаги (из TODO списка), Статус выполнения задач

### Community 38 - "Исправлено дублирование событий в Google Calendar"
Cohesion: 0.40
Nodes (4): Дополнительные рекомендации для полной уверенности:, Изменения в файле `app/google_calendar/service.py`:, Исправлено дублирование событий в Google Calendar, Как это решает проблему дублирования:

### Community 39 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 40 - "extends"
Cohesion: 0.50
Nodes (4): react-app, react-app/jest, eslintConfig, extends

### Community 48 - "hf"
Cohesion: 0.17
Nodes (17): bn(), ct(), dt(), et(), ft(), gt(), hf(), ht() (+9 more)

## Knowledge Gaps
- **151 isolated node(s):** `Config`, `Settings`, `short_name`, `name`, `icons` (+146 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `parse_ics()` connect `parse_ics` to `LessonData`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Why does `LessonData` connect `LessonData` to `parse_ics`, `mais_parser.py`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Why does `SyncService` connect `LessonData` to `main.py`, `UserStats`, `mais_parser.py`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `o()` (e.g. with `ad()` and `hd()`) actually correct?**
  _`o()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ss()` (e.g. with `a()` and `ao()`) actually correct?**
  _`ss()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `a()` (e.g. with `ad()` and `af()`) actually correct?**
  _`a()` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `rf()` (e.g. with `a()` and `d()`) actually correct?**
  _`rf()` has 9 INFERRED edges - model-reasoned connections that need verification._