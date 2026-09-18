# Graph Report - MAISync  (2026-09-17)

## Corpus Check
- 73 files · ~115,729 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 933 nodes · 2433 edges · 68 communities (59 shown, 9 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 195 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `37c73ce7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- LessonData
- ss
- main.74f1fbe2.js
- n
- App.js
- parse_ics
- telegram/service.py
- main.py
- l
- enterface.md
- s
- auth/service.py
- Lesson
- dependencies
- get_token_path
- mais_parser.py
- auth/schemas.py
- telegram_link
- Database
- post
- Xn
- package.json
- rd
- devDependencies
- development
- web/manifest.json
- User Guide
- public/manifest.json
- m
- EmailService
- Xu
- scripts
- extends
- MAISync
- MAISync
- MAISync logo (XO in black rounded rectangle)
- MAISync
- STATUS
- TODO
- README
- WEB
- nu
- nf
- Learn More
- diff.py
- calculate_diff
- Решение проблемы дублирования в Telegram боте
- Da
- Usage
- Анализ дублирования событий в Google Calendar
- Telegram Bot for XO_OS
- Исправлено дублирование событий в Google Calendar
- axios
- xo_os

## God Nodes (most connected - your core abstractions)
1. `l()` - 72 edges
2. `s()` - 61 edges
3. `n()` - 50 edges
4. `ss()` - 44 edges
5. `User` - 33 edges
6. `i()` - 32 edges
7. `hl()` - 29 edges
8. `rd()` - 27 edges
9. `Database` - 25 edges
10. `LessonData` - 25 edges

## Surprising Connections (you probably didn't know these)
- `test_user_creation()` --calls--> `Database`  [INFERRED]
  test_auth.py → app/database/db.py
- `test_user_creation()` --calls--> `UserCreate`  [INFERRED]
  test_auth.py → app/auth/schemas.py
- `test_password_hash()` --calls--> `get_password_hash()`  [INFERRED]
  test_auth.py → app/auth/service.py
- `test_user_creation()` --calls--> `create_user()`  [INFERRED]
  test_auth.py → app/auth/service.py
- `test_user_creation()` --calls--> `authenticate_user()`  [INFERRED]
  test_auth.py → app/auth/service.py

## Import Cycles
- None detected.

## Communities (68 total, 9 thin omitted)

### Community 0 - "LessonData"
Cohesion: 0.14
Nodes (19): UserStats, LessonData, Нормализованное занятие MAISync. source_uid: Оригинальный UID из ICS. Сохраняем…, Совместимость с предыдущей версией проекта. В будущем лучше везде перейти на…, Хэш всех изменяемых данных занятия. Если хэш поменялся — занятие необходимо…, DiffResult, LessonChange, Результат сравнения одного занятия. kind: CREATED UPDATED MOVED DELETED… (+11 more)

### Community 1 - "ss"
Cohesion: 0.05
Nodes (81): A(), Aa(), ai(), ao(), as(), ba(), bf(), Bi() (+73 more)

### Community 2 - "main.74f1fbe2.js"
Cohesion: 0.07
Nodes (27): Br(), Cr(), cs(), ds(), $f(), ge(), He(), hf() (+19 more)

### Community 3 - "n"
Cohesion: 0.11
Nodes (38): al(), At(), Cl(), clear(), De(), dl(), el(), fl() (+30 more)

### Community 4 - "App.js"
Cohesion: 0.08
Nodes (19): App(), Achievements(), CalendarObsidianBlock(), Header(), Login(), NowBlock(), PlayerCard(), ScheduleList() (+11 more)

### Community 5 - "parse_ics"
Cohesion: 0.11
Nodes (28): _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), Any, datetime (+20 more)

### Community 6 - "telegram/service.py"
Cohesion: 0.12
Nodes (29): TelegramLinkCode, error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files). (+21 more)

### Community 7 - "main.py"
Cohesion: 0.09
Nodes (41): get_user_from_session(), User, auth_status(), export_to_obsidian(), get_achievements(), get_current_active_user(), get_current_user(), get_current_user_info() (+33 more)

### Community 8 - "l"
Cohesion: 0.10
Nodes (35): af(), bd(), cd(), dd(), df(), Dr(), ef(), fd() (+27 more)

### Community 9 - "enterface.md"
Cohesion: 0.06
Nodes (32): 10. Расписание, 11. Следующее событие, 12. Главный статистический блок, 13. Динамика нагрузки, 14. Top Subjects, 15. План против факта, 16. Достижения, 17. Streak (+24 more)

### Community 10 - "s"
Cohesion: 0.17
Nodes (28): bt(), ct(), dt(), forEach(), fs(), gt(), ht(), jt() (+20 more)

### Community 11 - "auth/service.py"
Cohesion: 0.15
Nodes (24): UserCreate, authenticate_user(), confirm_email_change(), create_user(), delete_session(), get_password_hash(), initiate_email_change(), initiate_password_reset() (+16 more)

### Community 12 - "Lesson"
Cohesion: 0.12
Nodes (19): Base, Lesson, get_credentials_path(), get_data_dir(), get_google_calendar_service(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., Authenticates with Google Calendar API and returns a service object. Handles… (+11 more)

### Community 13 - "dependencies"
Cohesion: 0.10
Nodes (21): react, react-dom, react-icons, react-router-dom, react-scripts, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+13 more)

### Community 14 - "get_token_path"
Cohesion: 0.22
Nodes (9): get_token_path(), Returns the path to the Google OAuth2 token file., echo(), get_calendar_status(), google_callback(), google_status(), Handle Google OAuth2 callback., Check Google connection status. (+1 more)

### Community 15 - "mais_parser.py"
Cohesion: 0.16
Nodes (15): get_mais_groups(), import_mais_schedule(), Get list of MAIS groups., Import schedule for a given MAIS group name., _build_identity_key(), fetch_group_schedule(), fetch_groups(), _parse_date() (+7 more)

### Community 16 - "auth/schemas.py"
Cohesion: 0.39
Nodes (7): AuthStatusResponse, Config, BaseModel, TokenResponse, UserBase, UserLogin, UserResponse

### Community 17 - "telegram_link"
Cohesion: 0.28
Nodes (8): Создаёт одноразовый код привязки учетной записи Telegram и создаёт Telegram…, Unlink Telegram account., telegram_link(), telegram_unlink(), BaseModel, TelegramLinkResponse, TelegramStatusResponse, TelegramUnlinkResponse

### Community 18 - "Database"
Cohesion: 0.14
Nodes (17): build_parser(), cmd_export(), cmd_import_ics(), cmd_stats(), cmd_status(), main(), Export lessons to Obsidian., Show user statistics. (+9 more)

### Community 19 - "post"
Cohesion: 0.14
Nodes (20): create_session(), Session, confirm_email_change_endpoint(), google_disconnect(), initiate_email_change_endpoint(), initiate_password_reset_endpoint(), login(), Disconnect/revoke Google OAuth tokens. (+12 more)

### Community 20 - "Xn"
Cohesion: 0.10
Nodes (12): Gn(), Hn(), In(), Jn(), Kn(), nr(), Qn(), rr() (+4 more)

### Community 21 - "package.json"
Cohesion: 0.20
Nodes (9): author, description, keywords, license, main, name, private, proxy (+1 more)

### Community 22 - "rd"
Cohesion: 0.14
Nodes (23): ad(), An(), c(), d(), _e(), Fn(), hs(), id() (+15 more)

### Community 23 - "devDependencies"
Cohesion: 0.22
Nodes (9): autoprefixer, @craco/craco, postcss, devDependencies, autoprefixer, @craco/craco, postcss, tailwindcss (+1 more)

### Community 24 - "development"
Cohesion: 0.22
Nodes (9): >0.2%, last 1 chrome version, last 1 firefox version, last 1 safari version, not dead, not op_mini all, browserslist, development (+1 more)

### Community 25 - "web/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 26 - "User Guide"
Cohesion: 0.09
Nodes (21): API Description, Architecture Overview, CLI Commands, Conflict Resolution, Dependencies, Environment Variables, License, Main Components (+13 more)

### Community 27 - "public/manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 28 - "m"
Cohesion: 0.20
Nodes (21): ar(), b(), constructor(), et(), g(), h(), Ie(), k() (+13 more)

### Community 29 - "EmailService"
Cohesion: 0.13
Nodes (13): Settings, EmailService, Отправьте электронное письмо для сброса пароля. Args: email: адрес электронной…, Сервис для отправки писем по SMTP., Отправьте электронное письмо с запросом подтверждения смены email. Args: email:…, Отправьте электронное письмо с подтверждением новой электронной почты. Args:…, Render a Jinja2 template with the given context. Args: template_name: Name of…, Отправьте электронное письмо с подтверждением регистрации. Args: email: адрес… (+5 more)

### Community 30 - "Xu"
Cohesion: 0.19
Nodes (21): ac(), cc(), ce(), dc(), fc(), gc(), hc(), Hr() (+13 more)

### Community 31 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, eject, start, test

### Community 32 - "extends"
Cohesion: 0.50
Nodes (4): react-app, react-app/jest, eslintConfig, extends

### Community 33 - "MAISync"
Cohesion: 0.67
Nodes (3): App, MAISync, Web

### Community 53 - "nu"
Cohesion: 0.16
Nodes (20): au(), bc(), Be(), bs(), cu(), du(), ec(), eu() (+12 more)

### Community 54 - "nf"
Cohesion: 0.17
Nodes (17): ae(), ee(), eject(), gs(), ne(), nf(), Oe(), q() (+9 more)

### Community 55 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 56 - "diff.py"
Cohesion: 0.36
Nodes (10): _as_local(), _date_distance_days(), _find_best_match(), _lesson_score(), datetime, Оценивает вероятность того, что old и new — одно и то же занятие после…, Ищет лучшее fuzzy-сопоставление. Ограничиваем поиск 14 днями, чтобы не…, Приводит datetime к Europe/Moscow. SQLite может вернуть datetime без tzinfo… (+2 more)

### Community 57 - "calculate_diff"
Cohesion: 0.53
Nodes (9): calculate_diff(), Сравнивает старое состояние с новым. Алгоритм: 1. Exact match по identity_key.…, make_new(), make_old(), test_date_change_is_moved(), test_exact_identity_is_updated(), test_new_lesson_is_created(), test_time_change_is_moved() (+1 more)

### Community 58 - "Решение проблемы дублирования в Telegram боте"
Cohesion: 0.20
Nodes (9): Альтернативный подход (если subprocess нежелателен):, Анализ проблемы, Изменения в `app/telegram_bot.py`, Предлагаемое решение, Преимущества этого подхода:, Причина проблемы, Решение проблемы дублирования в Telegram боте, Следующие шаги: (+1 more)

### Community 59 - "Da"
Cohesion: 0.33
Nodes (3): Da(), oa(), za()

### Community 60 - "Usage"
Cohesion: 0.25
Nodes (7): Changes Made, Current State, Google Calendar Setup, Installation, Running, Usage, XO_OS - Google Calendar Integration Summary

### Community 61 - "Анализ дублирования событий в Google Calendar"
Cohesion: 0.29
Nodes (6): Анализ дублирования событий в Google Calendar, Как проверить, какой случай у вас есть:, Почему вы всё ещё видите дублирование:, Следующие шаги:, Что можно сделать:, Что я проверил и исправил:

### Community 62 - "Telegram Bot for XO_OS"
Cohesion: 0.29
Nodes (6): Direct URL fetch (optional), Forwarding from external bot, How it works, Setup, Telegram Bot for XO_OS, Usage

### Community 63 - "Исправлено дублирование событий в Google Calendar"
Cohesion: 0.40
Nodes (4): Дополнительные рекомендации для полной уверенности:, Изменения в файле `app/google_calendar/service.py`:, Исправлено дублирование событий в Google Calendar, Как это решает проблему дублирования:

## Knowledge Gaps
- **143 isolated node(s):** `Config`, `short_name`, `name`, `icons`, `start_url` (+138 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `LessonData`, `telegram/service.py`, `main.py`, `auth/service.py`, `Lesson`, `EmailService`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `parse_ics()` connect `parse_ics` to `LessonData`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `SyncService` connect `Database` to `LessonData`, `mais_parser.py`, `Lesson`, `main.py`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `l()` (e.g. with `b()` and `c()`) actually correct?**
  _`l()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `s()` (e.g. with `hd()` and `mf()`) actually correct?**
  _`s()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `n()` (e.g. with `ad()` and `ci()`) actually correct?**
  _`n()` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ss()` (e.g. with `i()` and `lo()`) actually correct?**
  _`ss()` has 2 INFERRED edges - model-reasoned connections that need verification._