# Graph Report - MAISync  (2026-09-18)

## Corpus Check
- 73 files · ~116,040 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 940 nodes · 2440 edges · 73 communities (64 shown, 9 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 195 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `37c73ce7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- LessonData
- l
- main.74f1fbe2.js
- i
- App.js
- parse_ics
- telegram/service.py
- main.py
- forEach
- enterface.md
- zd
- auth/service.py
- Lesson
- dependencies
- n
- mais_parser.py
- create_user
- ss
- Database
- post
- Xn
- package.json
- s
- devDependencies
- development
- web/manifest.json
- User Guide
- public/manifest.json
- rd
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
- ms
- Learn More
- diff.py
- calculate_diff
- Решение проблемы дублирования в Telegram боте
- Da
- Usage
- Анализ дублирования событий в Google Calendar
- Telegram Bot for XO_OS
- Исправлено дублирование событий в Google Calendar
- fi
- xo_os
- export_to_obsidian
- models.py
- Fixes Applied
- hc
- ls
- react-scripts

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
- `test_password_hash()` --calls--> `get_password_hash()`  [INFERRED]
  test_auth.py → app/auth/service.py
- `test_user_creation()` --calls--> `authenticate_user()`  [INFERRED]
  test_auth.py → app/auth/service.py
- `test_user_creation()` --calls--> `Database`  [INFERRED]
  test_auth.py → app/database/db.py
- `test_user_creation()` --calls--> `UserCreate`  [INFERRED]
  test_auth.py → app/auth/schemas.py
- `test_user_creation()` --calls--> `create_user()`  [INFERRED]
  test_auth.py → app/auth/service.py

## Import Cycles
- None detected.

## Communities (73 total, 9 thin omitted)

### Community 0 - "LessonData"
Cohesion: 0.15
Nodes (17): LessonData, Нормализованное занятие MAISync. source_uid: Оригинальный UID из ICS. Сохраняем…, Совместимость с предыдущей версией проекта. В будущем лучше везде перейти на…, Хэш всех изменяемых данных занятия. Если хэш поменялся — занятие необходимо…, DiffResult, LessonChange, Результат сравнения одного занятия. kind: CREATED UPDATED MOVED DELETED…, Человекочитаемое описание изменения. (+9 more)

### Community 1 - "l"
Cohesion: 0.14
Nodes (27): A(), bo(), co(), Do(), ei(), er(), fo(), fr() (+19 more)

### Community 2 - "main.74f1fbe2.js"
Cohesion: 0.08
Nodes (21): ad(), ba(), Br(), ge(), id(), Ja(), jc(), Jr() (+13 more)

### Community 3 - "i"
Cohesion: 0.13
Nodes (27): al(), bl(), Cl(), clear(), dl(), el(), fl(), Gr() (+19 more)

### Community 4 - "App.js"
Cohesion: 0.08
Nodes (19): App(), Achievements(), CalendarObsidianBlock(), Header(), Login(), NowBlock(), PlayerCard(), ScheduleList() (+11 more)

### Community 5 - "parse_ics"
Cohesion: 0.11
Nodes (28): _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), Any, datetime (+20 more)

### Community 6 - "telegram/service.py"
Cohesion: 0.13
Nodes (28): error_handler(), handle_document(), handle_link_code(), handle_start(), main(), process_ics_content(), Handle incoming document messages (expected to be ICS files)., Обработка Telegram deep-link: https://t.me/BOT_USERNAME?start=CODE Telegram… (+20 more)

### Community 7 - "main.py"
Cohesion: 0.08
Nodes (46): get_user_from_session(), User, get_token_path(), Returns the path to the Google OAuth2 token file., echo(), get_achievements(), get_calendar_status(), get_current_active_user() (+38 more)

### Community 8 - "forEach"
Cohesion: 0.14
Nodes (18): af(), df(), eject(), $f(), ff(), forEach(), hf(), hs() (+10 more)

### Community 9 - "enterface.md"
Cohesion: 0.06
Nodes (32): 10. Расписание, 11. Следующее событие, 12. Главный статистический блок, 13. Динамика нагрузки, 14. Top Subjects, 15. План против факта, 16. Достижения, 17. Streak (+24 more)

### Community 10 - "zd"
Cohesion: 0.15
Nodes (33): bt(), ct(), dt(), ef(), fd(), ft(), Gd(), gt() (+25 more)

### Community 11 - "auth/service.py"
Cohesion: 0.17
Nodes (21): UserLogin, authenticate_user(), confirm_email_change(), create_session(), delete_session(), get_password_hash(), initiate_email_change(), initiate_password_reset() (+13 more)

### Community 12 - "Lesson"
Cohesion: 0.13
Nodes (17): Lesson, get_credentials_path(), get_data_dir(), get_google_calendar_service(), Returns the directory where application data is stored. Uses the same directory…, Returns the path to the Google OAuth2 client secrets file., Authenticates with Google Calendar API and returns a service object. Handles…, _event_to_lesson_key() (+9 more)

### Community 13 - "dependencies"
Cohesion: 0.10
Nodes (21): axios, react, react-dom, react-icons, react-router-dom, @testing-library/dom, @testing-library/jest-dom, @testing-library/react (+13 more)

### Community 14 - "n"
Cohesion: 0.12
Nodes (29): ai(), bf(), ci(), componentDidCatch(), Dr(), eo(), gf(), Gu() (+21 more)

### Community 15 - "mais_parser.py"
Cohesion: 0.16
Nodes (15): get_mais_groups(), import_mais_schedule(), Get list of MAIS groups., Import schedule for a given MAIS group name., _build_identity_key(), fetch_group_schedule(), fetch_groups(), _parse_date() (+7 more)

### Community 16 - "create_user"
Cohesion: 0.21
Nodes (13): AuthStatusResponse, Config, BaseModel, TokenResponse, UserBase, UserCreate, UserResponse, create_user() (+5 more)

### Community 17 - "ss"
Cohesion: 0.23
Nodes (16): Bi(), ca(), es(), Fe(), ia(), Ir(), is(), ka() (+8 more)

### Community 18 - "Database"
Cohesion: 0.13
Nodes (19): build_parser(), cmd_export(), cmd_import_ics(), cmd_stats(), cmd_status(), main(), Export lessons to Obsidian., Show user statistics. (+11 more)

### Community 19 - "post"
Cohesion: 0.16
Nodes (16): confirm_email_change_endpoint(), google_disconnect(), initiate_email_change_endpoint(), initiate_password_reset_endpoint(), Disconnect/revoke Google OAuth tokens., Verify email using token from verification link., Resend verification email to user., Initiate password reset process. (+8 more)

### Community 20 - "Xn"
Cohesion: 0.09
Nodes (13): Gn(), Hn(), In(), Jn(), Kn(), Mn(), nr(), Qn() (+5 more)

### Community 21 - "package.json"
Cohesion: 0.20
Nodes (9): author, description, keywords, license, main, name, private, proxy (+1 more)

### Community 22 - "s"
Cohesion: 0.18
Nodes (19): Cr(), De(), _e(), fs(), He(), It(), ks(), Le() (+11 more)

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

### Community 28 - "rd"
Cohesion: 0.13
Nodes (37): An(), ar(), b(), bd(), c(), constructor(), d(), et() (+29 more)

### Community 29 - "EmailService"
Cohesion: 0.13
Nodes (13): Settings, EmailService, Отправьте электронное письмо для сброса пароля. Args: email: адрес электронной…, Сервис для отправки писем по SMTP., Отправьте электронное письмо с запросом подтверждения смены email. Args: email:…, Отправьте электронное письмо с подтверждением новой электронной почты. Args:…, Render a Jinja2 template with the given context. Args: template_name: Name of…, Отправьте электронное письмо с подтверждением регистрации. Args: email: адрес… (+5 more)

### Community 30 - "Xu"
Cohesion: 0.25
Nodes (16): ac(), At(), cc(), ce(), dc(), fc(), ic(), Ju() (+8 more)

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

### Community 54 - "ms"
Cohesion: 0.16
Nodes (20): ae(), cd(), cs(), dd(), ds(), ee(), gc(), gs() (+12 more)

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
Cohesion: 0.21
Nodes (5): Aa(), Da(), oa(), oi(), za()

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

### Community 64 - "fi"
Cohesion: 0.27
Nodes (15): ao(), di(), fi(), gi(), gl(), io(), La(), no() (+7 more)

### Community 67 - "export_to_obsidian"
Cohesion: 0.20
Nodes (10): export_to_obsidian(), get_current_user_info(), get_obsidian_path(), get_obsidian_vault_path(), logout(), Any, Экспортируйте занятия в Obsidian., Log out the current user. (+2 more)

### Community 68 - "models.py"
Cohesion: 0.33
Nodes (6): Base, Session, TelegramLinkCode, DeclarativeBase, Test password hashing directly, test_password_hash()

### Community 69 - "Fixes Applied"
Cohesion: 0.25
Nodes (7): 1. Email Verification Endpoint, 2. Registration Endpoint, 3. Import Alias, 4. Graph Update, Expected Results, Fixes Applied, Prerequisites

### Community 70 - "hc"
Cohesion: 0.33
Nodes (6): hc(), Hr(), ko(), pc(), so(), wo()

### Community 71 - "ls"
Cohesion: 0.50
Nodes (4): as(), ls(), Ra(), rs()

## Knowledge Gaps
- **149 isolated node(s):** `Config`, `short_name`, `name`, `icons`, `start_url` (+144 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `LessonData`, `models.py`, `telegram/service.py`, `main.py`, `Lesson`, `create_user`, `EmailService`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `parse_ics()` connect `parse_ics` to `LessonData`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `SyncService` connect `Database` to `LessonData`, `export_to_obsidian`, `main.py`, `Lesson`, `mais_parser.py`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `l()` (e.g. with `b()` and `c()`) actually correct?**
  _`l()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `s()` (e.g. with `hd()` and `mf()`) actually correct?**
  _`s()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `n()` (e.g. with `ad()` and `ci()`) actually correct?**
  _`n()` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ss()` (e.g. with `i()` and `lo()`) actually correct?**
  _`ss()` has 2 INFERRED edges - model-reasoned connections that need verification._