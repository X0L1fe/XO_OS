from __future__ import annotations

import logging
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from zoneinfo import ZoneInfo

from googleapiclient.errors import HttpError

from app.database.db import Database
from app.database.models import (
    GoogleCalendarConnection,
    GoogleCalendarEvent,
    Lesson,
    User,
)
from app.google_calendar.auth import get_google_calendar_service
from app.google_calendar.labels import (
    CUSTOM_SLOT_KEYS,
    build_all_labels,
    resolve_event_label_id,
)
from app.ics.parser import LessonData
from app.sync.diff import DiffResult, LessonChange

logger = logging.getLogger(__name__)


LOCAL_TIMEZONE = ZoneInfo("Europe/Moscow")

# Mapping from lesson_type to Google Calendar color ID.
LESSON_TYPE_COLOR_MAP = {
    "LECTURE": "xo_os_cocoa",
    "PRACTICE": "xo_os_mango",
    "LAB": "xo_os_banana",
    "EXAM": "xo_os_tomato",
}

# Mapping from lesson_type to Russian abbreviations for event title
LESSON_TYPE_ABBREVIATION_MAP = {
    "LECTURE": "ЛК",
    "PRACTICE": "ПЗ",
    "LAB": "ЛР",
    "EXAM": "Э",
}


def _parse_google_date_or_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """
    Parses a Google Calendar date or dateTime string into a timezone-aware datetime in UTC.
    Handles:
    - RFC3339 dateTime strings (with or without timezone, with Z or offset)
    - Date-only strings (YYYY-MM-DD) for all-day events, returned as 00:00:00 UTC
    Returns None if the string is empty or cannot be parsed.
    """
    if not dt_str:
        return None
    try:
        # If it ends with Z, replace with +00:00
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        dt = datetime.fromisoformat(dt_str)
        # Convert to UTC
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc)
        else:
            # No timezone info, assume UTC
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        # Try parsing as date only (YYYY-MM-DD)
        try:
            date = datetime.strptime(dt_str, "%Y-%m-%d").date()
            dt = datetime.combine(date, datetime.min.time()).replace(
                tzinfo=timezone.utc
            )
            return dt
        except ValueError:
            return None


def _event_to_lesson_key(event: dict) -> str | None:
    """
    Извлекает потенциальный идентификатор урока из события Google Calendar.
    Возвращает google_event_id, если мы можем идентифицировать его как наш, иначе None.
    """
    # Наши события должны иметь google_event_id, хранящийся в уроке,
    # но мы также можем попытаться идентифицировать по шаблонам описания/сummary, если необходимо.
    # Пока мы полагаемся на поле google_event_id в уроках.
    # Эта функция является placeholder'ом для более сложного matching при необходимости.
    return None


def _lesson_to_google_event(
    lesson: Lesson | LessonData,
    color_overrides: dict | None = None,
) -> dict:
    """
    Преобразует объект Lesson или LessonData в словарь события Google Calendar.
    color_overrides: пользовательские переопределения цветов вида
    {"LECTURE": null, "PRACTICE": 6, ...}. Если None — берутся дефолты.
    """
    # Убедимся, что объекты datetime осведомлены о часовом поясе (они должны быть).
    start = lesson.start_time
    end = lesson.end_time

    # Google Calendar ожидает timestamps в формате RFC3339.
    # Если временная метка без часового пояса, предполагаем локальное время.
    if start.tzinfo is None:
        start = start.replace(tzinfo=LOCAL_TIMEZONE)
    if end.tzinfo is None:
        end = end.replace(tzinfo=LOCAL_TIMEZONE)

    # Формируем заголовок: аббревиатура типа занятия + название предмета
    abbreviation = LESSON_TYPE_ABBREVIATION_MAP.get(lesson.lesson_type, "")
    subject = lesson.subject or ""
    if abbreviation and subject:
        summary = f"{abbreviation} {subject}"
    elif abbreviation:
        summary = abbreviation
    else:
        summary = subject

    # Формируем описание: аудитория на первой строке, преподаватель на второй
    description_parts = []
    if lesson.room:
        description_parts.append(lesson.room)
    if lesson.teacher:
        description_parts.append(lesson.teacher)
    description = "\n".join(description_parts)

    event = {
        "summary": summary,
        "location": "",  # Место проведения больше не используется (остается пустым)
        "description": description,
        "start": {
            "dateTime": start.isoformat(),
            "timeZone": str(LOCAL_TIMEZONE),
        },
        "end": {
            "dateTime": end.isoformat(),
            "timeZone": str(LOCAL_TIMEZONE),
        },
        # Напоминания можно настроить; используем значение по умолчанию.
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 24 * 60},  # 1 день до
                {"method": "popup", "minutes": 10},
            ],
        },
    }

    effective_map = {**LESSON_TYPE_COLOR_MAP, **(color_overrides or {})}
    value = effective_map.get(lesson.lesson_type)

    resolved = resolve_event_label_id(value)
    if resolved is not None:
        field, val = resolved
        event[field] = val

    # Добавляем участников, если есть преподаватели? Необязательно для now.
    # Мы могли бы добавить преподавателя как участника, но Google Calendar ожидает email-адреса.
    # Поскольку у нас нет email, пропускаем.

    return event


class GoogleCalendarSyncService:
    def __init__(
        self,
        db: Database,
        *,
        calendar_id: str | None = None,
        calendar_name: str = "primary",
        user_id: int,
    ):
        self.db = db
        self.user_id = user_id
        self.calendar_name = calendar_name

        # Загружаем пользовательские цвета один раз
        with self.db.session() as session:
            from app.database.models import User

            u = session.query(User).filter(User.id == user_id).first()
            self.color_overrides = (u.lesson_colors or {}) if u else {}

        if calendar_id is not None:
            self.calendar_id = calendar_id
        else:
            if calendar_name == "primary":
                self.calendar_id = "primary"
            else:
                service = get_google_calendar_service()
                calendar_list = service.calendarList().list().execute()

                for cal in calendar_list.get("items", []):
                    if cal.get("summary") == calendar_name:
                        self.calendar_id = cal["id"]
                        break
                else:
                    raise ValueError(
                        f"Calendar with name '{calendar_name}' "
                        "not found in your calendar list."
                    )

    def _fetch_google_events(
        self,
        service,
        time_min: datetime | None = None,
        time_max: datetime | None = None,
        sync_token: Optional[str] = None,
        show_deleted: bool = False,
    ) -> Tuple[List[dict], Optional[str]]:
        """
        Получает события из целевого календаря Google Calendar.
        Возвращает кортеж (список словарей событий, nextSyncToken).

        Args:
            service: Google Calendar service object
            time_min: Время начала для фильтрации событий (не используется с syncToken)
            time_max: Время конца для фильтрации событий (не используется с syncToken)
            sync_token: Токен синхронизации для инкрементальной синхронизации
            show_deleted: Показывать ли удаленные события (игнорируется с syncToken)

        Returns:
            Tuple[List[dict], Optional[str]]: (обогащенные события, nextSyncToken)
        """
        try:
            all_events = []
            request_params = {
                "calendarId": self.calendar_id,
                "singleEvents": True,
                "orderBy": "startTime",
            }

            # Если указан syncToken, используем его и игнорируем timeMin/timeMax/showDeleted
            if sync_token is not None:
                request_params["syncToken"] = sync_token
            else:
                # Для полной синхронизации используем обычные параметры
                if time_min:
                    request_params["timeMin"] = time_min.isoformat()
                if time_max:
                    request_params["timeMax"] = time_max.isoformat()
                if show_deleted:
                    request_params["showDeleted"] = "true"

            page_token = None
            next_sync_token = None
            while True:
                if page_token:
                    request_params["pageToken"] = page_token
                events_result = service.events().list(**request_params).execute()
                events = events_result.get("items", [])
                all_events.extend(events)
                page_token = events_result.get("nextPageToken")
                # nextSyncToken возвращается только в последней странице
                if "nextSyncToken" in events_result:
                    next_sync_token = events_result["nextSyncToken"]
                if not page_token:
                    break

            enriched_events = []
            for event in all_events:
                enriched = {
                    "id": event.get("id"),
                    "summary": event.get("summary"),
                    "start": event.get("start"),
                    "end": event.get("end"),
                    "created": event.get("created"),
                    "updated": event.get("updated"),
                    "status": event.get("status"),
                    "recurringEventId": event.get("recurringEventId"),
                    "originalStartTime": event.get("originalStartTime"),
                    "iCalUID": event.get("iCalUID"),
                }
                enriched_events.append(enriched)
            return enriched_events, next_sync_token
        except HttpError as error:
            print(f"Не удалось получить события из Google Calendar: {error}")
            raise

    def _is_event_created_after_connection(
        self, event: dict, connected_at: datetime
    ) -> bool:
        """
        Возвращает True, если событие Google Calendar было создано не ранее момента подключения календаря.
        Правила:
        - Если event['created'] отсутствует или None -> False.
        - Если строка event['created'] не может быть распарсена как RFC3339 -> False.
        - Сравнение выполняется в UTC (оба datetime должны быть timezone-aware).
        - Граница включительная: created == connected_at -> True.
        - Не использует start_time, endTime, updated или другие поля для определения момента подключения.
        """
        # Проверяем, что connected_at timezone-aware (как должно быть по модели)
        if connected_at.tzinfo is None:
            # Нарушение контракта: ожидается timezone-aware datetime.
            # Безопасно считаем событие не подходящим.
            return False

        event_created = event.get("created")
        if not event_created:
            return False

        # Преобразуем строку RFC3339 в datetime.
        # Google API возвращает вроде "2026-10-07T19:20:00.123Z" или с offset.
        created_dt = _parse_google_date_or_datetime(event_created)
        if created_dt is None:
            # Если не удалось распарсить, событие не подходит.
            return False

        # Сравниваем timestamps: созданное >= connected_at.
        # Поскольку оба aware, можно вычесть.
        return created_dt >= connected_at

    def _push_local_changes_to_google(self, diff: DiffResult) -> None:
        """
        Отправляет локальные изменения (created/updated/moved/deleted)
        в Google Calendar. Это "push" часть синхронизации.
        """
        try:
            service = get_google_calendar_service()
        except Exception as e:
            print(f"[SYNC] Не удалось аутентифицироваться в Google: {e}")
            return

        # CREATED — создаём события в Google для новых уроков
        for change in diff.created:
            if change.new is None:
                continue
            with self.db.session() as session:
                lesson_db = (
                    session.query(Lesson)
                    .filter(
                        Lesson.user_id == self.user_id,
                        Lesson.stable_id == change.new.identity_key,
                    )
                    .first()
                )
                if lesson_db is None or lesson_db.google_event_id:
                    continue
                try:
                    event = _lesson_to_google_event(lesson_db, self.color_overrides)
                    created = (
                        service.events()
                        .insert(
                            calendarId=self.calendar_id,
                            body=event,
                            eventLabelVersion=1,  # Цвета по HEX
                        )
                        .execute()
                    )
                    lesson_db.google_event_id = created.get("id")
                    color_val = event.get("eventLabelId") or event.get("colorId")
                    lesson_db.last_color_value = color_val
                    lesson_db.last_synced_at = datetime.now(timezone.utc)
                    lesson_db.last_synced_content_hash = lesson_db.content_hash
                    session.commit()
                    print(
                        f"[SYNC] Создано событие Google {lesson_db.google_event_id} для {lesson_db.subject}"
                    )
                except Exception as e:
                    print(
                        f"[SYNC] Не удалось создать событие для {lesson_db.subject}: {e}"
                    )

        # UPDATED и MOVED — обновляем существующие события
        for change in list(diff.updated) + list(diff.moved):
            if change.old is None:
                continue
            with self.db.session() as session:
                lesson_db = (
                    session.query(Lesson)
                    .filter(
                        Lesson.id == change.old.id,
                        Lesson.user_id == self.user_id,
                    )
                    .first()
                )
                if lesson_db is None or not lesson_db.google_event_id:
                    continue
                try:
                    event = _lesson_to_google_event(lesson_db, self.color_overrides)
                    service.events().update(
                        calendarId=self.calendar_id,
                        eventId=lesson_db.google_event_id,
                        body=event,
                        eventLabelVersion=1,
                    ).execute()
                    lesson_db.last_synced_at = datetime.now(timezone.utc)
                    lesson_db.last_synced_content_hash = lesson_db.content_hash
                    session.commit()
                    print(
                        f"[SYNC] Обновлено событие Google {lesson_db.google_event_id} для {lesson_db.subject}"
                    )
                except Exception as e:
                    print(
                        f"[SYNC] Не удалось обновить событие для {lesson_db.subject}: {e}"
                    )

        # DELETED — удаляем события из Google
        for change in diff.deleted:
            if change.old is None:
                continue
            # change.old — уже удалён из БД, но google_event_id доступен из памяти
            google_event_id = change.old.google_event_id
            if not google_event_id:
                continue
            try:
                service.events().delete(
                    calendarId=self.calendar_id,
                    eventId=google_event_id,
                ).execute()
                print(f"[SYNC] Удалено событие Google {google_event_id}")
            except Exception as e:
                print(f"[SYNC] Не удалось удалить событие: {e}")

    def _detect_and_handle_conflicts(
        self, service, google_events: list[dict] | None = None, session=None
    ) -> None:
        """
        Обнаруживает события в Google Calendar, у которых нет соответствующего локального урока,
        и уроки, у которых есть google_event_id, но события больше не существуют в Google Calendar.
        Автоматически разрешает конфликты:
        - Удаляет события в Google Calendar, которым не соответствует локальный урок.
        - Создает/обновляет события в Google Calendar для локальных уроков, у которых есть google_event_id,
          но события отсутствуют в календаре.
        """
        # Определяем кодировку консоли для безопасного вывода
        console_encoding = getattr(sys.stdout, "encoding", "utf-8")
        if console_encoding is None:
            console_encoding = "utf-8"

        def safe_str(s: str) -> str:
            """Возвращает строку, которую можно безопасно вывести в консоль."""
            if not isinstance(s, str):
                s = str(s)
            try:
                s.encode(console_encoding)
                return s
            except UnicodeEncodeError:
                # Заменяем непрорисовываемые символы на placeholder
                return s.encode(console_encoding, errors="replace").decode(
                    console_encoding
                )

        # Use provided session or create a new one
        session_provided = session is not None
        if not session_provided:
            session = self.db.session()

        try:
            # Получаем соединение для scoping уроков
            connection = (
                session.query(GoogleCalendarConnection)
                .filter(
                    GoogleCalendarConnection.user_id == self.user_id,
                    GoogleCalendarConnection.calendar_id == self.calendar_id,
                )
                .first()
            )

            # Формируем базовый запрос для уроков пользователя с google_event_id
            query = session.query(Lesson).filter(
                Lesson.user_id == self.user_id, Lesson.google_event_id.isnot(None)
            )

            # Если соединение найдено, добавляем scoping через GoogleCalendarEvent
            if connection is not None:
                query = query.join(
                    GoogleCalendarEvent,
                    Lesson.google_event_id == GoogleCalendarEvent.google_event_id,
                ).filter(GoogleCalendarEvent.connection_id == connection.id)

            lessons_with_ids = query.all()
            lesson_id_to_lesson = {
                lesson.google_event_id: lesson for lesson in lessons_with_ids
            }

            # Если события не переданы, получаем их из целевого календаря
            if google_events is None:
                google_events = self._fetch_google_events(service)
        finally:
            # Close session only if we created it
            if not session_provided:
                session.close()

            # Отслеживаем, какие google_event_ids мы уже увидели в Google Calendar
            seen_google_event_ids = set()

            # Проверяем каждое событие Google Calendar, соответствует ли оно локальному уроку
            for event in google_events:
                event_id = event.get("id")
                if event_id:
                    seen_google_event_ids.add(event_id)
                    if event_id not in lesson_id_to_lesson:
                        # Найдено событие в Google Calendar, которое не соответствует никакому локальному уроку.
                        # По правилам безопасности XO_OS не удаляет и не изменяет такие события.
                        event_summary = safe_str(event.get("summary", "Без названия"))
                        # Логируем для отладки, но не предпринимаем действий.
                        print(
                            f"[ИНФО] Обнаружено событие в Google Calendar без урока XO_OS: '{event_summary}' "
                            f"(ID: {event_id}). Оставляем без изменений."
                        )
                        # Опционально: извлечь больше деталей для журнала
                        start = event.get("start", {}).get(
                            "dateTime", event.get("start", {}).get("date")
                        )
                        end = event.get("end", {}).get(
                            "dateTime", event.get("end", {}).get("date")
                        )
                        print(f"       Время: {start} по {end}")

            # Проверяем уроки, у которых есть google_event_id, но события нет в Google Calendar
            for google_event_id, lesson in lesson_id_to_lesson.items():
                if google_event_id not in seen_google_event_ids:
                    # Урок считает, что имеет соответствующее событие в Google Calendar, но мы его не нашли
                    lesson_subject = safe_str(lesson.subject)
                    print(
                        f"[КОНФЛИКТ] Создаю/обновляю событие в Google Calendar для урока '{lesson_subject}' "
                        f"(ID: {lesson.id}) с google_event_id {google_event_id}, т.к. событие отсутствует."
                    )
                    print(
                        f"       Время урока: {lesson.start_time} по {lesson.end_time}"
                    )
                    try:
                        self.sync_lesson(lesson)
                        print(f"       Синхронизация урока {lesson.id} завершена.")
                    except Exception as error:
                        print(
                            f"       Не удалось синхронизировать урок {lesson.id}: {error}"
                        )

    def sync_changes(self, diff: DiffResult) -> None:
        """
        Синхронизирует изменения (созданные, обновленные, удаленные, перемещенные) в Google Calendar.
        Использует syncToken для инкрементальной синхронизации когда доступен.
        Выполняет полную синхронизацию когда syncToken отсутствует или недействителен.
        """
        # Получаем соединение для определения необходимости полной или инкрементальной синхронизации
        with self.db.session() as session:
            connection = (
                session.query(GoogleCalendarConnection)
                .filter(
                    GoogleCalendarConnection.user_id == self.user_id,
                    GoogleCalendarConnection.calendar_id == self.calendar_id,
                )
                .first()
            )

            # Если соединения нет, ничего не делаем
            if not connection:
                return
            sync_token = connection.sync_token

        # ----------------------------------------------------------------
        # PUSH: отправляем локальные изменения в Google Calendar
        # ----------------------------------------------------------------
        self._push_local_changes_to_google(diff)

        # ----------------------------------------------------------------
        # PULL: дальше существующая логика (is_incremental_sync, ...)
        # ----------------------------------------------------------------
        is_incremental_sync = sync_token is not None

        # Выполняем синхронизацию с обработкой повтора при 410 ошибке
        max_attempts = 2  # Одна попытка инкрементальной + одна попытка полной при 410
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            try:
                service = get_google_calendar_service()

                # Выполняем fetch событий
                if is_incremental_sync and attempt == 1:
                    # Первая попытка: инкрементальная синхронизация с сохраненным токеном
                    google_events, next_sync_token = self._fetch_google_events(
                        service, sync_token=connection.sync_token
                    )
                    sync_type = "incremental"
                else:
                    # Полная синхронизация (или повтор после 410)
                    google_events, next_sync_token = self._fetch_google_events(
                        service,
                        show_deleted=True,  # Важно: показываем удаленные события для корректной обработки отмененных
                    )
                    sync_type = "full"

                # Обрабатываем события в транзакции, чтобы обеспечить атомарность обновления токена
                with self.db.session() as session:
                    # Обновляем соединение внутри той же сессии
                    connection = (
                        session.query(GoogleCalendarConnection)
                        .filter(
                            GoogleCalendarConnection.user_id == self.user_id,
                            GoogleCalendarConnection.calendar_id == self.calendar_id,
                        )
                        .with_for_update()
                        .first()
                    )  # Блокируем строку для предотвращения гонок

                    if not connection:
                        return

                    # ПERSISTENCE: Сохраняем события Google Calendar, созданные после подключения
                    self._persist_google_events(connection, google_events, session)

                    # Handle cancelled events (статус='cancelled' в ответе Google Calendar)
                    # Для инкрементальной синхронизации НЕ обрабатываем отсутствующие события как удаленные
                    # Только события со статусом 'cancelled' рассматриваются как удаленные
                    self._handle_cancelled_google_events(
                        connection, google_events, session
                    )

                    # Обнаруживаем и обрабатываем конфликты (создание/обновление событий в Google Calendar для локальных уроков)
                    self._detect_and_handle_conflicts(
                        service, google_events=google_events, session=session
                    )

                    # Если дошли сюда без исключений, обновляем sync_token и фиксируем транзакцию
                    connection.sync_token = next_sync_token
                    session.commit()

                # Если успешно дошли до этой точки, прерываем цикл
                break

            except HttpError as error:
                if error.resp.status == 410 and is_incremental_sync and attempt == 1:
                    # Получили 410 Gone при инкрементальной синхронизации - пробуем полную синхронизацию еще раз
                    print(
                        "[ИНФО] Получен HTTP 410 при инкрементальной синхронизации, выполняем повторную полную синхронизацию..."
                    )
                    is_incremental_sync = (
                        False  # Переключаемся на полную синхронизацию во второй попытке
                    )
                    continue  # Переходим к следующей попытке (уже увеличен attempt)
                else:
                    # Другая ошибка или 410 при второй попытке (полной синхронизации) - пробрасываем наружу
                    print(f"Ошибка синхронизации: {error}")
                    raise
            except Exception as error:
                # Любая другая ошибка - пробрасываем наружу, не обновляя токен
                print(f"Неожиданная ошибка синхронизации: {error}")
                raise

    def sync_lesson(self, lesson: Lesson) -> None:
        """
        Синхронизируйте один урок с Календарем Google (создайте или обновите).
        Используется для начальной синхронизации или при изменении урока вне импорта ICS.
        """
        try:
            service = get_google_calendar_service()
        except Exception as e:
            print(f"Не удалось пройти аутентификацию в Google Calendar: {e}")
            return

        with self.db.session() as session:
            lesson_db = (
                session.query(Lesson)
                .filter(
                    Lesson.id == lesson.id,
                    Lesson.user_id == self.user_id,
                )
                .first()
            )
            if not lesson_db:
                return

            event = _lesson_to_google_event(lesson_db, self.color_overrides)
            if lesson_db.google_event_id:
                try:
                    service.events().update(
                        calendarId=self.calendar_id,
                        eventId=lesson_db.google_event_id,
                        body=event,
                        eventLabelVersion=1,
                    ).execute()
                    # Update last_syned_at and last_syned_content_hash after successful update.
                    lesson_db.last_synced_at = datetime.now(timezone.utc)
                    lesson_db.last_synced_content_hash = lesson_db.content_hash
                    session.commit()
                except HttpError as error:
                    print(
                        f"Не удалось обновить событие в Google Calendar для {lesson_db.subject}: {error}"
                    )
            else:
                try:
                    created_event = (
                        service.events()
                        .insert(
                            calendarId=self.calendar_id,
                            body=event,
                            eventLabelVersion=1,
                        )
                        .execute()
                    )
                    google_event_id = created_event.get("id")
                    print(
                        f"Создано событие Google {created_event.get('id')} для {lesson_db.subject}"
                    )
                    lesson_db.google_event_id = google_event_id
                    color_val = event.get("eventLabelId") or event.get("colorId")
                    lesson_db.last_color_value = color_val
                    lesson_db.last_synced_at = datetime.now(timezone.utc)
                    lesson_db.last_synced_content_hash = lesson_db.content_hash
                    session.commit()
                except HttpError as error:
                    print(
                        f"Не удалось создать событие в Google Calendar для {lesson_db.subject}: {error}"
                    )

    def sync_all_existing_lessons(self) -> int:
        """
        Создаёт события в Google для всех уроков пользователя,
        у которых google_event_id ещё не проставлен.
        Возвращает количество созданных событий.
        """
        try:
            service = get_google_calendar_service()
        except Exception as e:
            print(f"[SYNC] Не удалось аутентифицироваться в Google: {e}")
            return 0

        created_count = 0
        with self.db.session() as session:
            lessons = (
                session.query(Lesson)
                .filter(
                    Lesson.user_id == self.user_id,
                    Lesson.google_event_id.is_(None),
                )
                .all()
            )
            print(f"[SYNC] Найдено {len(lessons)} уроков без google_event_id")

            for lesson in lessons:
                try:
                    event = _lesson_to_google_event(lesson, self.color_overrides)
                    created = (
                        service.events()
                        .insert(
                            calendarId=self.calendar_id,
                            body=event,
                            eventLabelVersion=1,
                        )
                        .execute()
                    )
                    lesson.google_event_id = created.get("id")
                    color_val = event.get("eventLabelId") or event.get("colorId")
                    lesson.last_color_value = color_val
                    lesson.last_synced_at = datetime.now(timezone.utc)
                    lesson.last_synced_content_hash = lesson.content_hash
                    created_count += 1
                    print(
                        f"[SYNC] Создано событие {lesson.google_event_id} "
                        f"для {lesson.subject}"
                    )
                except Exception as e:
                    print(
                        f"[SYNC] Не удалось создать событие для {lesson.subject}: {e}"
                    )

            session.commit()

        return created_count

    @classmethod
    def refresh_colors_for_user(
        cls,
        db,
        user_id: int,
        calendar_id: str,
    ) -> int:
        """Фоновая задача после сохранения цветов."""
        try:
            svc = cls(
                db,
                calendar_id=calendar_id,
                user_id=user_id,
            )

            return svc.refresh_all_event_colors()
        except Exception as e:
            print(f"[SYNC] refresh_colors_for_user упал для user={user_id}: {e}")
            return 0

    @classmethod
    def initial_sync_for_user(
        cls,
        db: Database,
        user_id: int,
        calendar_id: str,
    ) -> int:
        """
        Точка входа для фоновой задачи после выбора календаря.
        Создаёт сервис и запускает первичную синхронизацию всех уроков.
        """
        try:
            svc = cls(db, calendar_id=calendar_id, user_id=user_id)
            svc.ensure_labels_registered()
            return svc.sync_all_existing_lessons()
        except Exception as e:
            print(f"[SYNC] initial_sync_for_user упал для user={user_id}: {e}")
            return 0

    def _persist_google_events(
        self,
        connection: GoogleCalendarConnection,
        google_events: list[dict],
        session=None,
    ) -> None:
        """
        Сохраняет события Google Calendar в локальную базу данных для данного соединения.
        Сохраняет только события, созданные после момента подключения (используя created timestamp).
        Теперь сохраняет как временные события, так и все дневные события.
        Учитывает флаг is_all_day для корректного представления все дневных событий.

        Args:
            connection: Объект GoogleCalendarConnection, представляющий соединение
            google_events: Список словарей событий из Google Calendar (already enriched with metadata)
        """
        from app.database.models import GoogleCalendarEvent

        # Use provided session or create a new one
        session_provided = session is not None
        if not session_provided:
            session_context = self.db.session()
            session = session_context.__enter__()

        try:
            for event in google_events:
                # Пропускаем события без ID
                event_id = event.get("id")
                if not event_id:
                    continue

                # Проверяем eligibility: событие должно быть создано не ранее подключения
                if not self._is_event_created_after_connection(
                    event, connection.connected_at
                ):
                    # Логируем событие, отброшенное из-за границы подключения
                    logger.info(
                        f"Skipping Google Calendar event due to connection boundary: "
                        f"connection_id={connection.id}, calendar_id={connection.calendar_id}, "
                        f"google_event_id={event_id}, event.created={event.get('created')}, "
                        f"connection.connected_at={connection.connected_at.isoformat()}, "
                        f'reason="created_before_connection"'
                    )
                    continue

                start_info = event.get("start", {})
                end_info = event.get("end", {})
                # Определяем, является ли событие все дневным
                # Для все дневных событий оба поля содержат 'date' (без 'dateTime')
                is_all_day = "date" in start_info and "date" in end_info

                # Преобразуем временные метки из RFC3339 в datetime objects (всегда в UTC)
                # Для все дневных событий используем поле 'date', для временных - 'dateTime'
                start_time = _parse_google_date_or_datetime(
                    start_info.get("dateTime") or start_info.get("date")
                )
                end_time = _parse_google_date_or_datetime(
                    end_info.get("dateTime") or end_info.get("date")
                )
                created_at_google = _parse_google_date_or_datetime(event.get("created"))
                updated_at_google = _parse_google_date_or_datetime(event.get("updated"))
                original_start_time = _parse_google_date_or_datetime(
                    event.get("originalStartTime")
                )

                # Если не удалось распарсить обязательные поля, пропускаем событие
                if start_time is None or end_time is None:
                    continue

                # Ищем существующее событие по (connection_id, google_event_id)
                existing_event = (
                    session.query(GoogleCalendarEvent)
                    .filter(
                        GoogleCalendarEvent.connection_id == connection.id,
                        GoogleCalendarEvent.google_event_id == event_id,
                    )
                    .first()
                )

                if existing_event:
                    # Обновляем существующее событие
                    existing_event.user_id = connection.user_id
                    existing_event.connection_id = connection.id
                    existing_event.calendar_id = connection.calendar_id
                    existing_event.summary = event.get("summary")
                    existing_event.start_time = start_time
                    existing_event.end_time = end_time
                    existing_event.created_at_google = created_at_google
                    existing_event.updated_at_google = updated_at_google
                    existing_event.status = event.get("status")
                    existing_event.recurring_event_id = event.get("recurringEventId")
                    existing_event.original_start_time = original_start_time
                    existing_event.i_cal_uid = event.get("iCalUID")
                    existing_event.is_all_day = is_all_day
                else:
                    # Создаем новое событие
                    new_event = GoogleCalendarEvent(
                        user_id=connection.user_id,
                        connection_id=connection.id,
                        google_event_id=event_id,
                        calendar_id=connection.calendar_id,
                        summary=event.get("summary"),
                        start_time=start_time,
                        end_time=end_time,
                        created_at_google=created_at_google,
                        updated_at_google=updated_at_google,
                        status=event.get("status"),
                        recurring_event_id=event.get("recurringEventId"),
                        original_start_time=original_start_time,
                        i_cal_uid=event.get("iCalUID"),
                        is_all_day=is_all_day,
                    )
                    session.add(new_event)
        finally:
            # Close session only if we created it
            if not session_provided:
                session_context.__exit__(None, None, None)

    def _handle_cancelled_google_events(
        self,
        connection: GoogleCalendarConnection,
        google_events: list[dict],
        session=None,
    ) -> None:
        """
        Handles cancelled Google Calendar events.
        For cancelled events (status='cancelled'), clears the google_event_id from local lessons.
        Does NOT handle deleted events by absence (that's only valid for full sync with showDeleted=true).
        In incremental sync, we rely solely on the status='cancelled' field in the response.

        Args:
            connection: Объект GoogleCalendarConnection, представляющий соединение
            google_events: Список словарей событий из Google Calendar (already enriched with metadata)
            session: SQLAlchemy session to use for database operations
        """
        from app.database.models import Lesson

        # Use provided session or create a new one
        session_provided = session is not None
        if not session_provided:
            session = self.db.session()

        try:
            # Get lessons for this user that have a google_event_id and are linked to this connection via GoogleCalendarEvent
            lessons_with_ids = (
                session.query(Lesson)
                .join(
                    GoogleCalendarEvent,
                    Lesson.google_event_id == GoogleCalendarEvent.google_event_id,
                )
                .filter(
                    Lesson.user_id == connection.user_id,
                    GoogleCalendarEvent.connection_id == connection.id,
                    Lesson.google_event_id.isnot(None),
                )
                .all()
            )
            lesson_id_to_lesson = {
                lesson.google_event_id: lesson for lesson in lessons_with_ids
            }

            # Process each event in the response
            for event in google_events:
                event_id = event.get("id")
                if not event_id:
                    continue

                # Если событие отменено, очищаем связанный локальный урок
                if event.get("status") == "cancelled":
                    if event_id in lesson_id_to_lesson:
                        lesson = lesson_id_to_lesson[event_id]
                        # Clear the google_event_id and update last_synced_at
                        lesson.google_event_id = None
                        lesson.last_synced_at = datetime.now(timezone.utc)
                        # Note: We do not clear content_hash or other fields; the lesson remains unchanged otherwise
                        # Add to session for update
                        session.add(lesson)
                        # Log for debugging
                        print(
                            f"[ИНФО] Отменённое событие Google {event_id} привело к очистке google_event_id для урока '{lesson.subject}'"
                        )
        finally:
            # Close session only if we created it
            if not session_provided:
                session.close()

    def ensure_labels_registered(self) -> None:
        """
        Регистрирует 24 палитровые метки + заданные кастомные метки
        в календаре пользователя.
        """
        try:
            service = get_google_calendar_service()
        except Exception as e:
            print(f"[SYNC] Не удалось аутентифицироваться: {e}")
            return

        with self.db.session() as session:
            user = session.query(User).filter(User.id == self.user_id).first()
            custom_colors = (user.custom_colors or {}) if user else {}

        labels = build_all_labels(custom_colors)

        try:
            result = (
                service.calendars()
                .patch(
                    calendarId=self.calendar_id,
                    body={"labelProperties": {"eventLabels": labels}},
                )
                .execute()
            )
            registered = result.get("labelProperties", {}).get("eventLabels", [])
            print(f"[SYNC] Зарегистрировано меток: {len(registered)} из {len(labels)}")

            if len(registered) < len(labels):
                print(
                    f"[SYNC] ВНИМАНИЕ: Google принял только {len(registered)} меток. "
                    f"Возможно, часть невалидна."
                )
        except Exception as e:
            print(f"[SYNC] Не удалось зарегистрировать метки: {e}")

    def refresh_all_event_colors(self) -> int:
        try:
            service = get_google_calendar_service()
        except Exception as e:
            print(f"[SYNC] Не удалось аутентифицироваться: {e}")
            return 0

        updated = 0
        skipped = 0
        with self.db.session() as session:
            lessons = (
                session.query(Lesson)
                .filter(
                    Lesson.user_id == self.user_id,
                    Lesson.google_event_id.isnot(None),
                )
                .all()
            )
            for lesson in lessons:
                event = _lesson_to_google_event(lesson, self.color_overrides)
                body = {}
                if "colorId" in event:
                    body["colorId"] = event["colorId"]
                if "eventLabelId" in event:
                    body["eventLabelId"] = event["eventLabelId"]

                if not body:
                    continue

                # Ключевое: значение цвета, которое должно быть в Google
                new_color_value = body.get("eventLabelId") or body.get("colorId")

                # Если уже такое же — пропускаем
                if lesson.last_color_value == new_color_value:
                    skipped += 1
                    continue

                try:
                    service.events().patch(
                        calendarId=self.calendar_id,
                        eventId=lesson.google_event_id,
                        body=body,
                        eventLabelVersion=1,
                    ).execute()
                    lesson.last_color_value = new_color_value
                    session.commit()
                    updated += 1
                    time.sleep(0.3)
                except HttpError as e:
                    if e.resp.status == 403:
                        print(f"[SYNC] Rate limit, пауза 30 сек...")
                        time.sleep(30)
                        try:
                            service.events().patch(
                                calendarId=self.calendar_id,
                                eventId=lesson.google_event_id,
                                body=body,
                                eventLabelVersion=1,
                            ).execute()
                            lesson.last_color_value = new_color_value
                            session.commit()
                            updated += 1
                        except Exception as e2:
                            print(f"[SYNC] Повтор не удался, пропускаю: {e2}")
                    else:
                        print(
                            f"[SYNC] Не удалось обновить цвет для {lesson.subject}: {e}"
                        )

        print(f"[SYNC] Обновлено: {updated}, пропущено (уже правильные): {skipped}")
        return updated
