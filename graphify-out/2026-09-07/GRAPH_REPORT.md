# Graph Report - MAISync  (2026-09-07)

## Corpus Check
- 57 files · ~101,074 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 729 nodes · 1624 edges · 53 communities (52 shown, 1 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 99 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- parse_ics
- google_calendar/service.py
- main.580390c4.js
- rf
- LessonData
- uu
- import_ics
- ed
- It
- yl
- XO_OS
- calculate_diff
- LessonChange
- o
- Usage
- Future Enhancements
- hu
- Xs
- qu
- co
- web/manifest.json
- xo_os
- main.py
- enterface.md
- App.js
- User Guide
- sync/service.py
- dependencies
- Learn More
- handle_document
- Решение проблемы дублирования в Telegram боте
- development
- XO_OS Web Version
- package.json
- manifest.json
- devDependencies
- Анализ дублирования событий в Google Calendar
- Telegram Bot for XO_OS
- Статус выполнения задач
- Исправлено дублирование событий в Google Calendar
- scripts
- extends

## God Nodes (most connected - your core abstractions)
1. `o()` - 69 edges
2. `uu()` - 40 edges
3. `a()` - 34 edges
4. `hu()` - 28 edges
5. `rf()` - 27 edges
6. `ma()` - 25 edges
7. `LessonData` - 22 edges
8. `Lesson` - 20 edges
9. `eu()` - 20 edges
10. `parse_ics()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `make_new()` --calls--> `LessonData`  [EXTRACTED]
  tests/test_diff.py → app/ics/parser.py
- `test_lab_multiple_teachers()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `test_lecture_parsing()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `GoogleCalendarSyncService` --uses--> `Database`  [INFERRED]
  app/google_calendar/service.py → app/database/db.py
- `test_create_update_and_delete()` --calls--> `Database`  [EXTRACTED]
  tests/test_sync.py → app/database/db.py

## Import Cycles
- None detected.

## Communities (53 total, 1 thin omitted)

### Community 0 - "parse_ics"
Cohesion: 0.11
Nodes (28): _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), Any, datetime (+20 more)

### Community 1 - "google_calendar/service.py"
Cohesion: 0.17
Nodes (12): get_google_calendar_service(), Authenticates with Google Calendar API and returns a service object. Handles…, _event_to_lesson_key(), GoogleCalendarSyncService, _lesson_to_google_event(), datetime, Получает события из целевого календаря Google Calendar. Возвращает список…, Обнаруживает события в Google Calendar, у которых нет соответствующего… (+4 more)

### Community 2 - "main.580390c4.js"
Cohesion: 0.07
Nodes (28): Ae(), at(), bd(), dd(), Dl(), ei(), fd(), Fe() (+20 more)

### Community 3 - "rf"
Cohesion: 0.13
Nodes (31): af(), An(), Cd(), d(), da(), Dn(), dr(), eu() (+23 more)

### Community 4 - "LessonData"
Cohesion: 0.21
Nodes (14): LessonData, Нормализованное занятие MAISync. source_uid: Оригинальный UID из ICS. Сохраняем…, Совместимость с предыдущей версией проекта. В будущем лучше везде перейти на…, Хэш всех изменяемых данных занятия. Если хэш поменялся — занятие необходимо…, _as_local(), _date_distance_days(), _find_best_match(), _lesson_score() (+6 more)

### Community 5 - "uu"
Cohesion: 0.06
Nodes (61): aa(), ai(), au(), ba(), Bi(), Br(), Ca(), ci() (+53 more)

### Community 6 - "import_ics"
Cohesion: 0.14
Nodes (15): export_to_obsidian(), get_obsidian_path(), get_obsidian_vault_path(), google_disconnect(), import_ics(), Any, Import an ICS file and sync to Google Calendar., Get saved Obsidian vault path. (+7 more)

### Community 7 - "ed"
Cohesion: 0.21
Nodes (15): bt(), ed(), gf(), is(), Jf(), nd(), nt(), os() (+7 more)

### Community 8 - "It"
Cohesion: 0.23
Nodes (12): bn(), et(), gt(), ht(), It(), kt(), mt(), pt() (+4 more)

### Community 9 - "yl"
Cohesion: 0.18
Nodes (11): bl(), df(), Do(), eo(), ff(), ke(), so(), vl() (+3 more)

### Community 10 - "XO_OS"
Cohesion: 0.33
Nodes (5): MVP 0.1, XO_OS, Архитектура, Запуск, Настройка Google Calendar

### Community 11 - "calculate_diff"
Cohesion: 0.53
Nodes (9): calculate_diff(), Сравнивает старое состояние с новым. Алгоритм: 1. Exact match по identity_key.…, make_new(), make_old(), test_date_change_is_moved(), test_exact_identity_is_updated(), test_new_lesson_is_created(), test_time_change_is_moved() (+1 more)

### Community 12 - "LessonChange"
Cohesion: 0.33
Nodes (3): LessonChange, Результат сравнения одного занятия. kind: CREATED UPDATED MOVED DELETED…, Человекочитаемое описание изменения.

### Community 22 - "o"
Cohesion: 0.19
Nodes (22): a(), ct(), dt(), ft(), hd(), hf(), _i(), ja() (+14 more)

### Community 24 - "Usage"
Cohesion: 0.25
Nodes (7): Changes Made, Current State, Google Calendar Setup, Installation, Running, Usage, XO_OS - Google Calendar Integration Summary

### Community 25 - "Future Enhancements"
Cohesion: 0.29
Nodes (6): Documentation, Future Enhancements, Google Calendar, Obsidian Integration, Scheduler, Statistics and Gamification

### Community 26 - "hu"
Cohesion: 0.18
Nodes (21): ac(), B(), bf(), cu(), du(), fu(), gu(), hu() (+13 more)

### Community 27 - "Xs"
Cohesion: 0.08
Nodes (45): ar(), bc(), _c(), cc(), dc(), De(), _e(), ec() (+37 more)

### Community 28 - "qu"
Cohesion: 0.16
Nodes (20): ad(), bu(), cs(), ds(), es(), fs(), ju(), ku() (+12 more)

### Community 29 - "co"
Cohesion: 0.13
Nodes (22): ao(), bo(), co(), fo(), gd(), go(), ho(), ii() (+14 more)

### Community 32 - "web/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 67 - "main.py"
Cohesion: 0.10
Nodes (32): get_credentials_path(), get_data_dir(), get_token_path(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., Returns the path to the Google OAuth2 token file., get_achievements(), get_calendar_status() (+24 more)

### Community 79 - "enterface.md"
Cohesion: 0.06
Nodes (32): 10. Расписание, 11. Следующее событие, 12. Главный статистический блок, 13. Динамика нагрузки, 14. Top Subjects, 15. План против факта, 16. Достижения, 17. Streak (+24 more)

### Community 89 - "App.js"
Cohesion: 0.10
Nodes (15): App(), Achievements(), CalendarObsidianBlock(), Header(), NowBlock(), PlayerCard(), ScheduleList(), Settings() (+7 more)

### Community 102 - "User Guide"
Cohesion: 0.09
Nodes (21): API Description, Architecture Overview, CLI Commands, Conflict Resolution, Dependencies, Environment Variables, License, Main Components (+13 more)

### Community 108 - "sync/service.py"
Cohesion: 0.13
Nodes (22): Settings, Database, Base, Lesson, Singleton table to store user's statistics and gamification data. Only one row…, UserStats, DiffResult, _apply_lesson_data() (+14 more)

### Community 117 - "dependencies"
Cohesion: 0.11
Nodes (19): react, react-dom, react-icons, react-scripts, @testing-library/dom, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event (+11 more)

### Community 148 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 170 - "handle_document"
Cohesion: 0.29
Nodes (9): error_handler(), handle_document(), main(), process_ics_content(), Log errors caused by updates., Handle incoming document messages (expected to be ICS files)., Process ICS content by delegating to the working xo-os import CLI. Optionally…, DEFAULT_TYPE (+1 more)

### Community 171 - "Решение проблемы дублирования в Telegram боте"
Cohesion: 0.20
Nodes (9): Альтернативный подход (если subprocess нежелателен):, Анализ проблемы, Изменения в `app/telegram_bot.py`, Предлагаемое решение, Преимущества этого подхода:, Причина проблемы, Решение проблемы дублирования в Telegram боте, Следующие шаги: (+1 more)

### Community 184 - "development"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 185 - "XO_OS Web Version"
Cohesion: 0.22
Nodes (8): API Endpoints, Dependencies, Development, Notes, Prerequisites, Project Structure, Running the Web Version, XO_OS Web Version

### Community 186 - "package.json"
Cohesion: 0.20
Nodes (9): author, description, keywords, license, main, name, private, proxy (+1 more)

### Community 191 - "manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 192 - "devDependencies"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 199 - "Анализ дублирования событий в Google Calendar"
Cohesion: 0.29
Nodes (6): Анализ дублирования событий в Google Calendar, Как проверить, какой случай у вас есть:, Почему вы всё ещё видите дублирование:, Следующие шаги:, Что можно сделать:, Что я проверил и исправил:

### Community 200 - "Telegram Bot for XO_OS"
Cohesion: 0.29
Nodes (6): Direct URL fetch (optional), Forwarding from external bot, How it works, Setup, Telegram Bot for XO_OS, Usage

### Community 202 - "Статус выполнения задач"
Cohesion: 0.33
Nodes (5): Выполнено, Как протестировать, Примечания, Следующие шаги (из TODO списка), Статус выполнения задач

### Community 207 - "Исправлено дублирование событий в Google Calendar"
Cohesion: 0.40
Nodes (4): Дополнительные рекомендации для полной уверенности:, Изменения в файле `app/google_calendar/service.py`:, Исправлено дублирование событий в Google Calendar, Как это решает проблему дублирования:

### Community 208 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 214 - "extends"
Cohesion: 0.50
Nodes (4): react-app, react-app/jest, eslintConfig, extends

## Knowledge Gaps
- **151 isolated node(s):** `Settings`, `short_name`, `name`, `icons`, `start_url` (+146 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `parse_ics()` connect `parse_ics` to `sync/service.py`, `LessonData`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Why does `LessonData` connect `LessonData` to `parse_ics`, `google_calendar/service.py`, `calculate_diff`, `sync/service.py`, `LessonChange`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Why does `SyncService` connect `sync/service.py` to `main.py`, `LessonData`, `LessonChange`, `import_ics`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `o()` (e.g. with `au()` and `hd()`) actually correct?**
  _`o()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `uu()` (e.g. with `a()` and `ao()`) actually correct?**
  _`uu()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `a()` (e.g. with `au()` and `_c()`) actually correct?**
  _`a()` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `rf()` (e.g. with `a()` and `d()`) actually correct?**
  _`rf()` has 9 INFERRED edges - model-reasoned connections that need verification._