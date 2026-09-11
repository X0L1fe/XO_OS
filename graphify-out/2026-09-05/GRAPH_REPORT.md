# Graph Report - MAISync  (2026-09-05)

## Corpus Check
- 36 files · ~36,562 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 453 nodes · 582 edges · 67 communities (46 shown, 21 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- parse_ics
- LessonData
- ChatGPT-Проектирование MAISync-20260905-1316.md
- GLOBAL CLAUDE CODE INSTRUCTIONS
- What You Must Do When Invoked
- 19. Что предлагаю сделать прямо сейчас
- 34. Итоговая версия MAISync
- diff.py
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- XO_OS
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- extraction-spec.md
- Структура проекта
- Usage
- Future Enhancements
- 32. И вот что я бы добавил сверх твоей идеи
- 10. А затем уже пишем первый код
- А теперь следующий этап
- Проектирование MAISync
- Следующее изменение будет уже серьёзным
- 2. Что конкретно мы теперь исправили
- 33. А ещё я бы сделал «уровень важности»
- 5. После этого запускаем
- 6. Я бы тогда сделал три источника данных
- Но уже сейчас можем начать проект
- И вот теперь можно начинать код
- И вот какой API я хочу получить в итоге
- Ещё одна идея для статистики, которая тебе может реально понравиться
- 10. Уведомления на телефон
- 1. Исправляем `tests/test_diff.py`
- 3. Я бы сделал уникальный ID для каждой пары
- 5. Как я предлагаю определять перенос
- 7. Сейчас ожидаемый результат
- 7. Что мы теперь получили
- Вариант, который я считаю оптимальным
- Поэтому меняем модель идентификации
- Но что делать с уведомлениями?
- 1. Исправляем parser
- 27. А вот пароль от ЛК я бы не хранил в обычном config.yaml
- 29. Я бы добавил CLI
- 2. Исправляем старый тест sync
- 2. Проверяем именно реальный кейс с двумя преподавателями
- 3. Исправляем warning в `app/ics/parser.py`
- 3. Исправляем тест `test_sync.py`
- 3. Но здесь обнаружилась ещё одна вещь
- 5. Военная кафедра - очень важный момент
- 5. Но в тесте есть небольшая проблема с `slots=True`
- 6. Но это нам нужно проверить
- 7. Теперь самое интересное — авторизация
- А вот `kk_access` надо исследовать
- Статистика
- Ещё важнее: недельный и семестровый UID разные
- Но нам нужно исследовать LOGIN
- Что я предлагаю сделать сейчас
- xo_os

## God Nodes (most connected - your core abstractions)
1. `LessonData` - 22 edges
2. `Lesson` - 19 edges
3. `parse_ics()` - 19 edges
4. `calculate_diff()` - 16 edges
5. `Database` - 15 edges
6. `LessonChange` - 14 edges
7. `DiffResult` - 14 edges
8. `SyncService` - 13 edges
9. `What You Must Do When Invoked` - 12 edges
10. `GoogleCalendarSyncService` - 11 edges

## Surprising Connections (you probably didn't know these)
- `make_new()` --calls--> `LessonData`  [EXTRACTED]
  tests/test_diff.py → app/ics/parser.py
- `test_lab_multiple_teachers()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `test_lecture_parsing()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py
- `test_create_update_and_delete()` --calls--> `Database`  [EXTRACTED]
  tests/test_sync.py → app/database/db.py
- `test_semester_filters_military()` --calls--> `parse_ics()`  [EXTRACTED]
  tests/test_ics_parser.py → app/ics/parser.py

## Import Cycles
- None detected.

## Communities (67 total, 21 thin omitted)

### Community 0 - "parse_ics"
Cohesion: 0.11
Nodes (28): Any, _build_identity_key(), _clean(), _detect_category(), _parse_datetime(), _parse_description(), parse_ics(), datetime (+20 more)

### Community 1 - "LessonData"
Cohesion: 0.07
Nodes (40): Settings, Database, Base, Lesson, get_credentials_path(), get_data_dir(), get_google_calendar_service(), get_token_path() (+32 more)

### Community 2 - "ChatGPT-Проектирование MAISync-20260905-1316.md"
Cohesion: 0.02
Nodes (80): 10. Тогда календарь становится не просто расписанием, 11. Obsidian здесь вообще отлично подходит, 11. А вот проверку я бы сделал немного умнее, 12. Но есть ещё более интересный вариант, 12. Тогда твой AI-агент получает совершенно другой уровень контекста, 13. Период расписания, 13. Причём агент не должен иметь прямой доступ ко всему компьютеру, 14. И можно сделать команды (+72 more)

### Community 3 - "GLOBAL CLAUDE CODE INSTRUCTIONS"
Cohesion: 0.12
Nodes (15): GLOBAL CLAUDE CODE INSTRUCTIONS, graphify, graphify, Выполняю, Диагностика, Команды, Ответы, Работа с кодом (+7 more)

### Community 4 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (26): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+18 more)

### Community 5 - "19. Что предлагаю сделать прямо сейчас"
Cohesion: 0.15
Nodes (13): 19. Что предлагаю сделать прямо сейчас, 1. Почему появился `maisync.egg-info/tests`, 2. Исправим `utcnow()`, Prompt:, Prompt:, Prompt:, Prompt:, Response: (+5 more)

### Community 6 - "34. Итоговая версия MAISync"
Cohesion: 0.17
Nodes (12): 34. Итоговая версия MAISync, Backend - FastAPI или Django, Prompt:, Response:, И самое главное, Что меняем, Этап 1 - MAI Parser, Этап 2 - Database (+4 more)

### Community 7 - "diff.py"
Cohesion: 0.23
Nodes (19): _as_local(), calculate_diff(), _date_distance_days(), _find_best_match(), _lesson_score(), datetime, Оценивает вероятность того, что old и new — одно и то же занятие после…, Ищет лучшее fuzzy-сопоставление. Ограничиваем поиск 14 днями, чтобы не… (+11 more)

### Community 8 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 9 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 10 - "XO_OS"
Cohesion: 0.33
Nodes (5): MVP 0.1, XO_OS, Архитектура, Запуск, Настройка Google Calendar

### Community 11 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 12 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 13 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 22 - "Структура проекта"
Cohesion: 0.20
Nodes (10): Prompt:, Prompt:, Response:, Response:, Важно, Первый этап, С чего реально начинаем, Структура проекта (+2 more)

### Community 24 - "Usage"
Cohesion: 0.25
Nodes (7): Changes Made, Current State, Google Calendar Setup, Installation, Running, Usage, XO_OS - Google Calendar Integration Summary

### Community 25 - "Future Enhancements"
Cohesion: 0.29
Nodes (6): Documentation, Future Enhancements, Google Calendar, Obsidian Integration, Scheduler, Statistics and Gamification

### Community 26 - "32. И вот что я бы добавил сверх твоей идеи"
Cohesion: 0.33
Nodes (6): 1. Расписание экзаменов, 2. Отмена занятия, 32. И вот что я бы добавил сверх твоей идеи, 3. Перенос, 4. Замена преподавателя, 5. Замена аудитории

### Community 27 - "10. А затем уже пишем первый код"
Cohesion: 0.40
Nodes (5): 10. А затем уже пишем первый код, Prompt:, Response:, Итого сейчас, Что видно из заголовков

### Community 28 - "А теперь следующий этап"
Cohesion: 0.40
Nodes (5): Prompt:, Response:, А теперь следующий этап, Пришли реальный `.ics` от бота МАИ, Что реально отдаёт бот МАИ

### Community 29 - "Проектирование MAISync"
Cohesion: 0.50
Nodes (4): 1. Как я вижу итоговую систему, Prompt:, Response:, Проектирование MAISync

### Community 30 - "Следующее изменение будет уже серьёзным"
Cohesion: 0.50
Nodes (4): 1. Файл `app/ics/parser.py`, Prompt:, Response:, Следующее изменение будет уже серьёзным

### Community 31 - "2. Что конкретно мы теперь исправили"
Cohesion: 0.50
Nodes (4): 2. Что конкретно мы теперь исправили, Военная подготовка, Время, Преподаватели

### Community 32 - "33. А ещё я бы сделал «уровень важности»"
Cohesion: 0.50
Nodes (4): 33. А ещё я бы сделал «уровень важности», CRITICAL, INFO, WARNING

### Community 33 - "5. После этого запускаем"
Cohesion: 0.50
Nodes (4): 5. После этого запускаем, Prompt:, Response:, Но здесь есть ещё одна проблема, которую я специально пока не стал скрывать

### Community 34 - "6. Я бы тогда сделал три источника данных"
Cohesion: 0.50
Nodes (4): 6. Я бы тогда сделал три источника данных, Google Calendar, MAISync, Obsidian

### Community 35 - "Но уже сейчас можем начать проект"
Cohesion: 0.50
Nodes (4): `auth.py`, `client.py`, `schemas.py`, Но уже сейчас можем начать проект

### Community 36 - "И вот теперь можно начинать код"
Cohesion: 0.50
Nodes (4): Prompt:, Response:, И вот теперь можно начинать код, Что происходит сейчас

### Community 37 - "И вот какой API я хочу получить в итоге"
Cohesion: 0.50
Nodes (4): Prompt:, Response:, И вот какой API я хочу получить в итоге, Следующий шаг

### Community 38 - "Ещё одна идея для статистики, которая тебе может реально понравиться"
Cohesion: 0.50
Nodes (4): Ещё одна идея для статистики, которая тебе может реально понравиться, Осталось, Плановая, Уже прошло

### Community 39 - "10. Уведомления на телефон"
Cohesion: 0.67
Nodes (3): 10. Уведомления на телефон, Вариант №1 - Telegram, Вариант №2 - Push

### Community 40 - "1. Исправляем `tests/test_diff.py`"
Cohesion: 0.67
Nodes (3): 1. Исправляем `tests/test_diff.py`, Но я хочу поправить один момент, Файл

### Community 41 - "3. Я бы сделал уникальный ID для каждой пары"
Cohesion: 0.67
Nodes (3): 3. Я бы сделал уникальный ID для каждой пары, Идентичность занятия, Содержимое занятия

### Community 42 - "5. Как я предлагаю определять перенос"
Cohesion: 0.67
Nodes (3): 5. Как я предлагаю определять перенос, Новое, Старое

### Community 43 - "7. Сейчас ожидаемый результат"
Cohesion: 0.67
Nodes (3): 7. Сейчас ожидаемый результат, Prompt:, Response:

### Community 44 - "7. Что мы теперь получили"
Cohesion: 0.67
Nodes (3): 7. Что мы теперь получили, Prompt:, Response:

### Community 45 - "Вариант, который я считаю оптимальным"
Cohesion: 0.67
Nodes (3): Вариант, который я считаю оптимальным, На ноутбуке:, Самая важная проблема - ноутбук выключен

### Community 46 - "Поэтому меняем модель идентификации"
Cohesion: 0.67
Nodes (3): Если UID изменился, Поэтому меняем модель идентификации, Сначала

### Community 47 - "Но что делать с уведомлениями?"
Cohesion: 0.67
Nodes (3): Критичные изменения, Но что делать с уведомлениями?, Обычные изменения

## Knowledge Gaps
- **253 isolated node(s):** `Settings`, `xo_os`, `graphify`, `Язык`, `Работа с кодом` (+248 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `19. Что предлагаю сделать прямо сейчас` connect `19. Что предлагаю сделать прямо сейчас` to `ChatGPT-Проектирование MAISync-20260905-1316.md`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `34. Итоговая версия MAISync` connect `34. Итоговая версия MAISync` to `ChatGPT-Проектирование MAISync-20260905-1316.md`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `Структура проекта` connect `Структура проекта` to `ChatGPT-Проектирование MAISync-20260905-1316.md`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `LessonData` (e.g. with `GoogleCalendarSyncService` and `DiffResult`) actually correct?**
  _`LessonData` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `Lesson` (e.g. with `GoogleCalendarSyncService` and `DiffResult`) actually correct?**
  _`Lesson` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Database` (e.g. with `Base` and `GoogleCalendarSyncService`) actually correct?**
  _`Database` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Settings`, `xo_os`, `graphify` to the rest of the system?**
  _253 weakly-connected nodes found - possible documentation gaps or missing edges._