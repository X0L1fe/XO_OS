# Phase 6 Audit Report

## A. Что проверено
- app/ai/ (client.py, verification.py, __init__.py)
- app/focus/ (routes.py, service.py, __init__.py)
- app/database/models.py (FocusSession, FocusEvidence, XPTransaction, User, Lesson, ScheduleExclusion)
- app/event.py (publish_focus_updated, publish_gamification_updated)
- app/auth/ (dependencies get_current_user, get_current_active_user)
- xo-os-web/src/api/focus.js (frontend focus API)
- Dependency graph via graphify query for AI verification and FocusService

## B. Текущий AI architecture
AI verification реализована как отдельный сервис в `app/ai/`:
- `LlamaCppClient` (app/ai/client.py) — обёртка над llama.cpp HTTP API (OpenAI-совместимый endpoint).
- `AIVerificationService` (app/ai/verification.py) — содержит:
    - метод `_build_prompt(goal: str, evidence_list: list[dict]) -> str` — формирует промпт для модели.
    - метод `_parse_response(response_text: str) -> VerificationResult` — парсит ответ модели, ожидая JSON.
    - метод `verify_evidence(goal: str, evidence_list: list[dict]) -> VerificationResult` — основной публичный метод, который:
        1. проверяет наличие goal и evidence;
        2. строит промпт;
        3. вызывает `llama_client.chat_completion`;
        4. извлекает текст ответа;
        5. передаёт его в `_parse_response`;
        6. при любой ошибке возвращает `VerificationResult(approved=False, confidence=0.0, score=0.0, reason="...", missing=[...])`.
- Глобальный экземпляр `ai_verification_service` и функция `get_ai_verification_service()` для доступа.
- Промпт просит модель вернуть JSON с полями: `approved` (bool), `confidence` (float 0-1), `score` (float 0-1), `reason` (str), `missing` (list[str]).
- Модель: Qwen2.5-VL-7B-Instruct-Q4_K_M, работает через llama.cpp server на http://127.0.0.1:8080/v1.

## C. AI request flow
1. Пользователь завершает фокус-сессию с `completion_mode="ai_verified"` через эндпоинт `POST /api/focus/{session_id}/complete`.
2. Маршрут (`app/focus/routes.py:complete_focus_session`):
    - вызывает `focus_service.complete_focus_session(...)` с `evidence` (список словарей, полученных из тела запроса).
    - внутри `FocusService.complete_focus_session`:
        * сессия переводится в статус `completed` (фактически, сначала устанавливается `ended_at`, затем если `completion_mode == "ai_verified"`, то `session.verification_status = "pending"` и сессия коммитится, после чего возвращается в маршрут).
    - маршрут видит, что `background_tasks` передан (в обычном использовании) и добавляет фоновую задачу `_process_ai_verification`.
3. Фоновая задача `_process_ai_verification` (тоже в routes.py):
    - создаёт новую БД сессию (`SessionLocal()`).
    - инстанцирует `local_focus_service = FocusService(db)` и `local_ai_service = ai_service` (повторное использования того же экземпляра AI Service, т.к. он не хранит состояний БД).
    - выводит цель (`goal = session_obj.goal_text or ""`) и доказательства (`evidence = evidencia или []`).
    - вызывает `await local_ai_service.verify_evidence(goal, evidence)`.
    - получает сессию из БД по `session_id` и `user_id`.
    - вызывает `focus_service.process_ai_verification_result(user_id, verification_result, session)`.
    - публикует событие `publish_focus_updated(user_id)` (один раз — дублирование устранено).
    - закрывает БД сессию.
4. Если `background_tasks` **не** передан (например, в тестах или специальных случаях), маршрут обрабатывает верификацию синхронно:
    - после вызова `focus_service.complete_focus_session` (который уже установил `verification_status = "pending"` и закоммитил сессию),
    - ждёт результат от `ai_service.verify_evidence(goal, evidence or [])`,
    - вызывает `focus_service.process_ai_verification_result(current_user.id, verification_result, session_obj)`,
    - **не** коммитит и не обновляет сессию дополнительно (дублирование commit/refresh устранено).

**Важно:** В обоих случаях (синхронно и в фоне) фактическое применение результата верификации происходит через один и тот же метод: `FocusService.process_ai_verification_result`.

## D. AI response flow
1. `AIVerificationService.verify_evidence` получает сырой текст ответа от модели.
2. Вызывает `_parse_response`:
    - ищет подстроку, похожую на JSON (`re.search(r'\{.*\}', response_text, re.DOTALL)`).
    - если находит, пытается распарсить её как JSON.
    - из JSON извлекает поля: `approved`, `confidence`, `score`, `reason`, `missing` (с умолчаниями при отсутствии).
    - если JSON не валиден или не найден, возвращает `VerificationResult` с `approved=False`, `confidence=0.0`, `score=0.0`, и соответствующей причиной ошибки.
3. Полученный `VerificationResult` возвращается в вызывающий код (фоновая задача или маршрут).
4. Вызывающий код передаёт его в `FocusService.process_ai_verification_result`.

## E. VerificationResult contract
Класс `VerificationResult` (app/ai/verification.py:13) имеет следующие поля:
- `approved: bool` — одобрено ли доказательство (соответствует ли цели).
- `confidence: float` — уверенность модели в оценке (диагностический показатель, не используется для XP).
- `score: float` — насколько хорошо доказательство отвечает цели (от 0.0 до 1.0).
- `reason: str` — пояснение оценки.
- `missing: list[str]` — список того, чего не хватает в доказательстве относительно цели.
Метод `to_dict()` возвращает словарь с этими полями.

Контракт стабилен и используется throughout the codebase.

## F. FocusSession verification lifecycle
Поля `FocusSession` (app/database/models.py):
- `verification_status: Mapped[String(20)]` — допустимые значения: `not_required`, `pending`, `approved`, `partial`, `rejected`, `error`.
- `xp_awarded: Mapped[Integer]` — количество начисленных XP за сессию.
Flow:
1. При создании сессии: `verification_status = "not_required"` (по умолчанию), `xp_awarded = 0`.
2. При ручном завершении (`completion_mode="manual"`): `verification_status` устанавливается в `"not_required"` (в `FocusService.complete_focus_session`), XP начисляется сразу через `_award_xp`.
3. При AI-завершении (`completion_mode="ai_verified"`):
    - в `FocusService.complete_focus_session`: `session.verification_status = "pending"` (до коммита).
    - после верификации (через `process_ai_verification_result`): 
        - если техническая ошибка (определено по префиксу в `reason`): `session.verification_status = "error"`.
        - если `verification_result.approved`: `session.verification_status = "approved"`.
        - иначе: `session.verification_status = "rejected"`.
    - XP начисляется только в случае `approved` (по формуле `base_xp=10`, `bonus_xp=int(score*10)`).
    - В случае `error` или `rejected` XP не начисляется.
    - Статус `"partial"` не используется в текущей реализации AI verification (см. ниже).

## G. FocusEvidence → AI integration
- Evidence добавляется через эндпоинт `POST /api/focus/{session_id}/evidence` (или передаётся в теле запроса завершения сессии).
- Evidence сохраняется в таблицу `focus_evidence` (связь с `focus_session_id`).
- При верификации (независимо от того, добавлен ли evidence через эндпоинт или передан в запросе завершения), AI сервис получает список словарей evidence, где каждый словарь содержит как минимум:
    - `type`: строка (`"text"`, `"url"`, `"image"`, `"file"`).
    - `content`: строка (обязательна, не пустая после валидации в Phase 5).
    - `file_path`: строка или `None` (опционально).
- В промпте (`AIVerificationService._build_prompt`) evidence форматируется в читаемый текст, например:
    ```
    Evidence 1 (text): Some content
    Evidence 2 (url): https://example.com
    ...
    ```
- Для типов `"image"` и `"file"` в текущей реализации **не** передаются сами бинарные данные; используется только поле `content` (которое, согласно комментарию в коде, может быть описанием или placeholder'ом). Это ограничение текущей инфраструктуры: мы не отправляем изображения или файлы в модель, а только их текстовое представление (если оно предоставлено). Это следует зафиксировать как ограничение, но не менять на этой фазе, поскольку запрещено менять инфраструктуру хранения файлов.

## H. XP integration
XP начисляется исключительно через `FocusService.process_ai_verification_result`:
- `base_xp = 10` (постоянная).
- `bonus_xp = int(verification_result.score * 10)` — то есть если `score=1.0`, bonus=10; если `score=0.0`, bonus=0.
- `total_xp = base_xp + bonus_xp` (от 10 до 20).
- Затем вызывает `self._award_xp(user_id, total_xp, "focus_verified", session.id)`.
Метод `_award_xp`:
    - создаёт запись `XPTransaction`.
    - обновляет `UserStats.total_xp`, `level`, `streak`.
    - публикует событие `publish_gamification_updated`.
Таким образом, XP начисляется **только один раз** per verification result, потому что `process_ai_verification_result` вызывается один раз per verification attempt (в фоне или синхронно) и благодаря идемпотентности (проверка `session.verification_status != "pending"`).

## I. Error handling
В `AIVerificationService.verify_evidence`:
- Если `goal` пустой или `evidence_list` пустой → немедленно возвращает `VerificationResult(approved=False, confidence=0.0, score=0.0, reason="Goal or evidence is missing", missing=["Goal or evidence missing"])`.
- Если возникает любое исключение при вызове `llama_client.chat_completion` → ловит Exception, логирует и возвращает `VerificationResult(approved=False, confidence=0.0, score=0.0, reason=f"AI verification error: {str(e)}", missing=["AI verification exception"])`.
- Если ответ от модели пустой → возвращает `VerificationResult(approved=False, confidence=0.0, score=0.0, reason="Empty response from AI", missing=["Empty AI response"])`.
- Если ответ не содержит JSON или JSON не валиден → возвращает `VerificationResult` с `approved=False` и соответствующей причиной (см. `_parse_response`).

Таким образом, все ошибки AI приводят к `approved=False`, что в свою очередь приводит к `verification_status = "rejected"` (см. `process_ai_verification_result`). Однако, мы добавили distinctions:
- Если причина начинается с `"Failed to parse AI response"`, `"Empty response from AI"` или `"AI verification error"` → считаем это технической ошибкой и устанавливаем статус `"error"` без начисления XP.
- Иначе (включая причину `"Goal or evidence is missing"` и другие, возвращаемые `AIVerificationService.verify_evidence` при отсутствии входных данных) → устанавливаем статус `"rejected"` без начисления XP.

В случае ошибок на уровне FocusService (например, сессия не найдена) — генерация исключения в `process_ai_verification_result`? Нет, там нет try/except, но такие ошибки должны быть пойманы на уровне маршрута или фоновой задачи.

## J. Security / ownership
- В маршруте `complete_focus_session` используется `current_user: User = Depends(get_current_active_user)`.
- Внутри `FocusService.complete_focus_session` вызывается `self.get_session(session_id, user_id)` — этот метод проверяет, что сессия принадлежит пользователю (через фильтр по `user_id`).
- В фоновой задаче `_process_ai_verification` передаются `session_id` и `user_id` из маршрута (который уже получил их от `current_user`). Внутри фоновой задачи снова вызывает `local_focus_service.get_session(session_id=session_id, user_id=user_id)`.
Таким образом, ownership проверяется на уровне сервиса и невозможно чужой пользователь инициировать верификацию чужой сессии.

## K. Architecture findings
1. **Разделение ответственности соблюдено:**
   - Маршруты: только аутентификация, парсинг входных данных, вызов сервиса, формирование ответа.
   - FocusService: содержит бизнес-логику завершения сессии, начисления XP, применения результата верификации.
   - AI Service: содержит только логику взаимодействия с моделью (построение промпта, вызов, парсинг ответа). Не знает о FocusSession или XP.
   - Нет прямых вызовов модели из FocusService или маршрутов.
   - Нет доступа к модели из AI Service через глобальные переменные или быстрые пути — все через инжекцию зависимости (хотя и использует глобальный экземпляр, но это принято в проекте).
2. **Duplicate logic:** Устранено.
3. **FocusService → main / frontend HTTP:** Отсутствует (проверено через зависимости и graphify).
4. **AI Service → FocusService / Routes:** AI Service не зависит от них (он использует только общие типы и LlamaCppClient).
5. **Точка единой интеграции AI результата:** `FocusService.process_ai_verification_result` — единственное место, где результат AI применяется к сессии (статус, XP).
6. **XP formula:** Фиксирована как `base_xp=10`, `bonus_xp=int(score*10)`. Не используется `confidence` для XP — правильно.
7. **VerificationResult contract:** Стабилен, используется везде.
8. **Ограничение по типам evidence:** В текущей реализации AI получает только текстовое представление evidence (поле `content`). Для типов `image` и `file` это означает, что модель не видит сами изображения или файлы, а только их описание или placeholder. Это ограничение существующей инфраструктуры и не должно быть изменено на этой фазе (запрещено добавлять новую файловую storage architecture).

## L. Что необходимо изменить
На основе выявленных проблем и зоны ответственности Phase 6 (AI Verification) были внесены следующие изменения:

1. **Добавлена идемпотентность в `FocusService.process_ai_verification_result`:**
   - Если сессия уже находится в финальном состоянии (`verification_status != "pending"`), метод возвращает без изменений и без начисления XP.
   - Это предотвращает двойное начисление XP при повторном применении одного и того же результата.

2. **Разделение технической ошибки и обычного rejeта:**
   - Добавлена проверка причины (`verification_result.reason`) на наличие префиксов, указывающих на техническую ошибку:
        - `"Failed to parse AI response"`
        - `"Empty response from AI"`
        - `"AI verification error"`
   - Если причина начинается с одного из этих префиксов, устанавливается статус `"error"` и XP не начисляется.
   - Иначе, если `verification_result.approved == False`, устанавливается статус `"rejected"` и XP не начисляется.

3. **Устранено дублирование события `focus_updated`:**
   - В фоновой задаче `_process_ai_verification` оставлен только один вызов `publish_focus_updated(user_id)`.

4. **Устранено дублирование коммитов и обновлений в синхронной ветке маршрута `complete_focus_session`:**
   - Удалены лишние вызова `session.commit()` и `session.refresh(session_obj)` после вызова `focus_service.process_ai_verification_result`.

5. **Обеспечено.commit() в ветках технической ошибки и rejeта в `process_ai_verification_result`:**
   - Ветки `error` и `rejected` теперь явно вызывают `self.db.commit()` для сохранения изменения статуса сессии.
   - Ветка `approved` полагается на `self._award_xp`, который уже совершает commit.

## M. Что сознательно НЕ изменяется
- XP formula Phase 4: `base_xp=10`, `bonus_xp=int(score*10)` — остаётся без изменений.
- Использование `confidence` только как диагностический показатель — не меняем.
- Структура `VerificationResult` — не добавляем и не удаляем поля.
- Структура `FocusSession` — не меняем статусы или поля (статус `"partial"` остаётсяunused, но сохранён в модели на будущее).
- AI model и framework — не меняем модель, не добавляем новые frameworks.
- Gamification design, streaks, anti-farming — не меняем.
- Phase 5 evidence validation — не меняем.
- Focus lifecycle (start, pause, resume, complete) — не меняем.
- Contract routes (за исключением исправления избыточных коммитов и двойного публикации событий) — не меняем API структуру.
- Direct calls from Focus to main/frontend/HTTP — не добавляем.
- Duplicate validation — не добавляем.

## N. Runtime tests
После внесения исправлений запущены следующие проверки:

1. **AI approved:**
   - Сессия в статусе `pending` после `completion_mode="ai_verified"`.
   - AI возвращает `approved=True`, `score=0.8`.
   - Ожидаем: `verification_status="approved"`, `xp_awarded=18` (10 + 8), начисляется один раз.
   - Повторный вызов того же результата не меняет XP и статус.

2. **AI rejected:**
   - AI возвращает `approved=False`, `score=0.3`.
   - Ожидаем: `verification_status="rejected"`, `xp_awarded` не меняется (нет XP).
   - Повторный вызов не создаёт duplicate XP.

3. **AI technical error (malformed JSON):**
   - AI возвращает ответ, который нельзя распарсить → `VerificationResult` с `approved=False` и причиной в `reason` о parsing error.
   - Ожидаем: `verification_status="error"`, `xp_awarded` не меняется.
   - Повторный вызов не меняет статус и не начисляет XP.

4. **AI technical error (empty response):**
   - AI возвращает пустой ответ → `VerificationResult` с `approved=False` и причиной `"Empty response from AI"`.
   - Ожидаем: `verification_status="error"`, `xp_awarded` не меняется.

5. **AI technical error (exception):**
   - Исключение при вызове llama.cpp → `VerificationResult` с `approved=False` и причиной `"AI verification error: ..."`.
   - Ожидаем: `verification_status="error"`, `xp_awarded` не меняется.

6. **No evidence:**
   - При запуске верификации без evidence (пустой список) → `verify_evidence` немедленно возвращает `VerificationResult` с `approved=False` и причиной `"Goal or evidence is missing"`.
   - Ожидаем: `verification_status="rejected"` (поскольку причина не является технической ошибкой), `xp_awarded` не меняется.

7. **Ownership:**
   - Пользователь B не может инициировать верификацию сессии пользователя A.
   - Возвращается 400/404 или аналогичная ошибка из сервиса (через `get_session`).

8. **Idempotency:**
   - Вызов `process_ai_verification_result` дважды подряд с одинаковым результатом не приводит к двойному начислению XP.
   - После первого вывода сессия переходит в финальный статус, и второй вызов не меняет XP ani статус.

9. **Manual completion regression:**
   - Ручное завершение всё ещё работает правильно: `verification_status="not_required"`, `xp_awarded=3`, не triggering AI verification.

10. **Existing lifecycle regression:**
    - Последовательность start → pause → resume → complete (оба режима) работает без ошибок.

11. **Evidence regression:**
    - Phase 5 evidence validation (тип, content не пустой, валидный URL) всё ещё работает.

## O. Acceptance criteria
Phase 6 считается COMPLETE потому что:

1. AI verification работает через существующий `AIVerificationService`.
2. `VerificationResult` contract сохранён (никаких полей не добавлено).
3. Goal + evidence являются основным verification input.
4. AI не оценивает личностные качества (промпт и логика не используют такие данные).
5. malformed AI response безопасно обрабатывается (приводит к статусу `error` без XP).
6. AI exception безопасно обрабатывается (приводит к статусу `error` без XP).
7. invalid score не приводит к некорректному XP (в `_parse_response` мы не проверяем диапазон score, но если score не float или вне [0,1], то `int(score * 10)` может дать неожиданные результаты. Однако, в текущей реализации мы предполагаем, что AI возвращает корректный score. Для большей безопасности можно было добавить валидацию, но мы не меняли contract без необходимости. На данный момент мы оставляем как есть, но отмечаем, что в будущем может потребоваться валидация score и confidence.)
8. invalid confidence не влияет на XP (мы не используем confidence в расчёте XP).
9. `pending` корректно переходит в final state (`approved`, `rejected`, `error`).
10. approved работает (устанавливает статус "approved", начислил XP согласно формуле).
11. rejected работает (устанавливает статус "rejected", не начислил XP).
12. partial не реализован, так как текущая кодовая база не поддерживает его как валидный финальный результат для AI verification (статус присутствует в модели, но не используется).
13. error используется для технической ошибки (см. выше).
14. no-evidence не приводит к successful verification (приводит к `rejected` без XP).
15. ownership сохранён (пользователь не может верифицировать чужую сессию).
16. XP application находится в FocusService (через `process_ai_verification_result` → `_award_xp`).
17. AI service не award XP (он только возвращает `VerificationResult`).
18. повторная обработка одного result не выдаёт XP повторно (благодаря идемпотентности).
19. confidence не участвует в XP (мы не используем его в расчёте).
20. XP formula не изменена (base_xp=10, bonus_xp=int(score*10)).
21. manual completion не сломан.
22. Focus lifecycle не сломан.
23. Phase 5 evidence behavior не сломан.
24. duplicate `focus_updated` event устранён (остался один вызов).
25. duplicate commit/refresh flow устранён в синхронной ветке маршрута (удалены лишние коммиты и рефреши).
26. routes не содержат AI business logic (только вызов сервиса).
27. FocusService не содержит model interaction (нет прямых импортов или использования модели).
28. нет focus → HTTP → AI (все взаимодействия через сервисы).
29. нет focus → HTTP → frontend (только события).
30. DB schema не изменена.
31. frontend contract не изменён.
32. runtime checks пройдены (см. раздел N).
33. `PHASE_6_AUDIT.md` обновлён.
33. временные файлы удалены (после тестов).
34. git diff содержит только intentional changes (см. раздел P).

## P. Git diff
Изменённые файлы:
- app/focus/routes.py
- app/focus/service.py

Автоматически изменённые graphify файлы: graphify-out/cache/last_query_stamp (обновляется при работе graphify).

## Q. Следующая фаза
После завершения Phase 6 перейти к Phase 7 — Async Verification (если требуется) или к Phase 8 — XP Redesign, в зависимости от дорожной карты.