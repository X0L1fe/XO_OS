from __future__ import annotations

import logging
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from googleapiclient.errors import HttpError

from app.database.db import Database
from app.database.models import Lesson
from app.google_calendar.auth import get_google_calendar_service
from app.ics.parser import LessonData
from app.sync.diff import LessonChange, DiffResult

logger = logging.getLogger(__name__)


LOCAL_TIMEZONE = ZoneInfo("Europe/Moscow")

# Mapping from lesson_type to Google Calendar color ID.
# Leave empty for default color (no colorId set).
LESSON_TYPE_COLOR_MAP = {
    "LECTURE": None,   # обычные пары ЛК - нет изменения цвета
    "PRACTICE": 3,     # ПЗ - глициния (цвет ID 3: Grape)
    "LAB": 5,          # ЛР - лимон (цвет ID 5: Banana)
    "EXAM": 11,        # Э - помидор (цвет ID 11: Tomato)
}


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


def _lesson_to_google_event(lesson: Lesson | LessonData) -> dict:
    """
    Преобразует объект Lesson или LessonData в словарь события Google Calendar.
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

    event = {
        "summary": lesson.subject,
        "location": lesson.room or "",
        "description": lesson.description or "",
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

    # Определяем цвет события по типу занятия.
    color_id = LESSON_TYPE_COLOR_MAP.get(lesson.lesson_type)
    if color_id is not None:
        event["colorId"] = str(color_id)

    # Добавляем участников, если есть преподаватели? Необязательно для now.
    # Мы могли бы добавить преподавателя как участника, но Google Calendar ожидает email-адреса.
    # Поскольку у нас нет email, пропускаем.

    return event


class GoogleCalendarSyncService:
    def __init__(self, db: Database, calendar_name: str = "primary"):
        self.db = db
        self.calendar_name = calendar_name
        if calendar_name == "primary":
            self.calendar_id = "primary"
        else:
            # Resolve the calendar name to an ID
            service = get_google_calendar_service()
            calendar_list = service.calendarList().list().execute()
            for cal in calendar_list.get('items', []):
                if cal.get('summary') == calendar_name:
                    self.calendar_id = cal['id']
                    break
            else:
                raise ValueError(f"Calendar with name '{calendar_name}' not found in your calendar list.")

    def _fetch_google_events(self, service, time_min: datetime | None = None, time_max: datetime | None = None) -> list[dict]:
        """
        Получает события из целевого календаря Google Calendar.
        Возвращает список словарей событий.
        """
        try:
            events_result = service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min.isoformat() if time_min else None,
                timeMax=time_max.isoformat() if time_max else None,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            return events_result.get('items', [])
        except HttpError as error:
            print(f"Не удалось получить события из Google Calendar: {error}")
            return []

    def _detect_and_handle_conflicts(self, service) -> None:
        """
        Обнаруживает события в Google Calendar, у которых нет соответствующего локального урока,
        и уроки, у которых есть google_event_id, но события больше не существуют в Google Calendar.
        Автоматически разрешает конфликты:
        - Удаляет события в Google Calendar, которым не соответствует локальный урок.
        - Создает/обновляет события в Google Calendar для локальных уроков, у которых есть google_event_id,
          но события отсутствуют в календаре.
        """
        # Определяем кодировку консоли для безопасного вывода
        console_encoding = getattr(sys.stdout, 'encoding', 'utf-8')
        if console_encoding is None:
            console_encoding = 'utf-8'

        def safe_str(s: str) -> str:
            """Возвращает строку, которую можно безопасно вывести в консоль."""
            if not isinstance(s, str):
                s = str(s)
            try:
                s.encode(console_encoding)
                return s
            except UnicodeEncodeError:
                # Заменяем непрорисовываемые символы на placeholder
                return s.encode(console_encoding, errors='replace').decode(console_encoding)

        with self.db.session() as session:
            # Получаем все уроки, у которых есть google_event_id
            lessons_with_ids = session.query(Lesson).filter(Lesson.google_event_id.isnot(None)).all()
            lesson_id_to_lesson = {lesson.google_event_id: lesson for lesson in lessons_with_ids}

            # Получаем все события из целевого календаря (можно ограничить разумным временным диапазоном)
            # Для простоты получаем все события - в продакшене возможно стоит ограничить по диапазону дат
            google_events = self._fetch_google_events(service)

            # Отслеживаем, какие google_event_ids мы уже увидели в Google Calendar
            seen_google_event_ids = set()

            # Проверяем каждое событие Google Calendar, соответствует ли оно локальному уроку
            for event in google_events:
                event_id = event.get('id')
                if event_id:
                    seen_google_event_ids.add(event_id)
                    if event_id not in lesson_id_to_lesson:
                        # Найдено событие в Google Calendar, которое не соответствует никакому локальному уроку
                        event_summary = safe_str(event.get('summary', 'Без названия'))
                        print(f"[КОНФЛИКТ] Удаляю событие в Google Calendar '{event_summary}' "
                              f"(ID: {event_id}), т.к. нет соответствующего локального урока.")
                        # Опционально: извлечь больше деталей для журнала
                        start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
                        end = event.get('end', {}).get('dateTime', event.get('end', {}).get('date'))
                        print(f"       Время: {start} по {end}")
                        try:
                            service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
                            print(f"       Событие {event_id} успешно удалено.")
                        except HttpError as error:
                            print(f"       Не удалось удалить событие {event_id}: {error}")

            # Проверяем уроки, у которых есть google_event_id, но события нет в Google Calendar
            for google_event_id, lesson in lesson_id_to_lesson.items():
                if google_event_id not in seen_google_event_ids:
                    # Урок считает, что имеет соответствующее событие в Google Calendar, но мы его не нашли
                    lesson_subject = safe_str(lesson.subject)
                    print(f"[КОНФЛИКТ] Создаю/обновляю событие в Google Calendar для урока '{lesson_subject}' "
                          f"(ID: {lesson.id}) с google_event_id {google_event_id}, т.к. событие отсутствует.")
                    print(f"       Время урока: {lesson.start_time} по {lesson.end_time}")
                    try:
                        self.sync_lesson(lesson)
                        print(f"       Синхронизация урока {lesson.id} завершена.")
                    except Exception as error:
                        print(f"       Не удалось синхронизировать урок {lesson.id}: {error}")

    def sync_changes(self, diff: DiffResult) -> None:
        """
        Синхронизирует изменения (созданные, обновленные, удаленные, перемещенные) в Google Calendar.
        """
        try:
            service = get_google_calendar_service()
        except Exception as e:
            # Если аутентификация не удалась, мы не можем синхронизировать. Записываем в лог и возвращаем.
            # В реальном приложении мы могли бы возбудить исключение или сохранить состояние ошибки.
            print(f"Не удалось пройти аутентификацию в Google Calendar: {e}")
            return

        # Сначала обнаруживаем и логируем любые конфликты между локальными уроками и событиями Google Calendar
        self._detect_and_handle_conflicts(service)

        
        # Process created lessons: create new events.
        for change in diff.created:
            assert change.new is not None
            lesson_data = change.new
            event = _lesson_to_google_event(lesson_data)
            try:
                # Avoid duplicate creation if google_event_id already exists (should not happen in created diff)
                with self.db.session() as session:
                    lesson = session.query(Lesson).filter(Lesson.stable_id == lesson_data.identity_key).first()
                    if lesson and lesson.google_event_id:
                        print(f"Пропущено создание события для {lesson_data.subject}: уже существует google_event_id {lesson.google_event_id}")
                        continue

                created_event = service.events().insert(calendarId=self.calendar_id, body=event).execute()
                google_event_id = created_event.get("id")
                print(f"Создано событие Google {created_event.get('id')} для {lesson_data.subject}")
                # Update the lesson in DB with the Google event ID and last synced content hash.
                with self.db.session() as session:
                    # Find the lesson by stable_id (identity_key) that was just created.
                    # The lesson should already be in the DB after the import_ics step.
                    lesson = session.query(Lesson).filter(Lesson.stable_id == lesson_data.identity_key).first()
                    if lesson:
                        lesson.google_event_id = google_event_id
                        lesson.last_synced_content_hash = lesson_data.content_hash
                        session.commit()
            except HttpError as error:
                print(f"Не удалось создать событие в Google Calendar для {lesson_data.subject}: {error}")

        # Process updated lessons: update existing events.
        for change in diff.updated:
            assert change.old is not None and change.new is not None
            lesson_data = change.new
            with self.db.session() as session:
                lesson = session.query(Lesson).filter(Lesson.stable_id == lesson_data.identity_key).first()
                event = _lesson_to_google_event(lesson_data)
                if lesson and lesson.google_event_id:
                    # Skip update if content hasn't changed since last sync.
                    if lesson.last_synced_content_hash is not None and lesson.content_hash == lesson.last_synced_content_hash:
                        print(f"Пропущено обновление события для {lesson_data.subject}: содержимое не изменилось с последней синхронизации.")
                    else:
                        try:
                            service.events().update(
                                calendarId=self.calendar_id,
                                eventId=lesson.google_event_id,
                                body=event,
                            ).execute()
                            print(f"Обновлено событие Google {lesson.google_event_id} для {lesson_data.subject}")
                            # Update last_synced_at and last_synced_content_hash after successful update.
                            lesson.last_synced_at = datetime.now(timezone.utc)
                            lesson.last_synced_content_hash = lesson_data.content_hash
                            session.commit()
                        except HttpError as error:
                            if error.resp.status == 404:
                                # Event not found in target calendar, fall through to create
                                pass
                            else:
                                print(f"Не удалось обновить событие в Google Calendar для {lesson_data.subject}: {error}")
                # Either no google_event_id, or update failed with 404 (event not found in target calendar)
                if not (lesson and lesson.google_event_id):
                    try:
                        created_event = service.events().insert(calendarId=self.calendar_id, body=event).execute()
                        google_event_id = created_event.get("id")
                        print(f"Создано событие Google {created_event.get('id')} для {lesson_data.subject}")
                        if lesson:
                            lesson.google_event_id = google_event_id
                            lesson.last_synced_at = datetime.now(timezone.utc)
                            lesson.last_synced_content_hash = lesson_data.content_hash
                            session.commit()
                    except HttpError as error:
                        print(f"Не удалось создать событие в Google Calendar для {lesson_data.subject}: {error}")

        # Process moved lessons: same as updated (time changed) but we already handle via update.
        # The diff already separates moved, but the Google Calendar event update will handle time change.
        for change in diff.moved:
            assert change.old is not None and change.new is not None
            lesson_data = change.new
            with self.db.session() as session:
                lesson = session.query(Lesson).filter(Lesson.stable_id == lesson_data.identity_key).first()
                event = _lesson_to_google_event(lesson_data)
                if lesson and lesson.google_event_id:
                    # Skip update if content hasn't changed since last sync.
                    if lesson.last_synced_content_hash is not None and lesson.content_hash == lesson.last_synced_content_hash:
                        print(f"Пропущено обновление события для {lesson_data.subject}: содержимое не изменилось с последней синхронизации.")
                    else:
                        try:
                            service.events().update(
                                calendarId=self.calendar_id,
                                eventId=lesson.google_event_id,
                                body=event,
                            ).execute()
                            print(f"Обновлено событие Google {lesson.google_event_id} для {lesson_data.subject}")
                            # Update last_synced_at and last_synced_content_hash after successful update.
                            lesson.last_synced_at = datetime.now(timezone.utc)
                            lesson.last_synced_content_hash = lesson_data.content_hash
                            session.commit()
                        except HttpError as error:
                            if error.resp.status == 404:
                                # Event not found in target calendar, fall through to create
                                pass
                            else:
                                print(f"Не удалось переместить событие в Google Calendar для {lesson_data.subject}: {error}")
                # Either no google_event_id, or update failed with 404 (event not found in target calendar)
                if not (lesson and lesson.google_event_id):
                    event = _lesson_to_google_event(lesson_data)
                    try:
                        created_event = service.events().insert(calendarId=self.calendar_id, body=event).execute()
                        google_event_id = created_event.get("id")
                        print(f"Создано событие Google {created_event.get('id')} для {lesson_data.subject}")
                        if lesson:
                            lesson.google_event_id = google_event_id
                            lesson.last_synced_at = datetime.now(timezone.utc)
                            lesson.last_synced_content_hash = lesson_data.content_hash
                            session.commit()
                    except HttpError as error:
                        print(f"Не удалось создать событие в Google Calendar для {lesson_data.subject}: {error}")

        # Process deleted lessons: delete events.
        for change in diff.deleted:
            assert change.old is not None
            lesson = change.old
            with self.db.session() as session:
                # Re-fetch to ensure we have the google_event_id.
                lesson_db = session.query(Lesson).filter(Lesson.id == lesson.id).first()
                if lesson_db and lesson_db.google_event_id:
                    try:
                        service.events().delete(
                            calendarId=self.calendar_id,
                            eventId=lesson_db.google_event_id,
                        ).execute()
                        # Clear the Google event ID after deletion.
                        lesson_db.google_event_id = None
                        # Update last_synced_at to mark that we've handled deletion.
                        lesson_db.last_synced_at = datetime.now(timezone.utc)
                        session.commit()
                    except HttpError as error:
                        print(f"Не удалось удалить событие в Google Calendar для {lesson.subject}: {error}")

        # Process unchanged lessons that lack Google event ID: create them.
        for change in diff.unchanged:
            assert change.old is not None and change.new is not None
            lesson_data = change.new
            with self.db.session() as session:
                lesson = session.query(Lesson).filter(Lesson.stable_id == lesson_data.identity_key).first()
                if lesson and lesson.google_event_id is None:
                    event = _lesson_to_google_event(lesson_data)
                    try:
                        created_event = service.events().insert(calendarId=self.calendar_id, body=event).execute()
                        google_event_id = created_event.get("id")
                        print(f"Создано событие Google {created_event.get('id')} для {lesson_data.subject} (was missing ID)")
                        if lesson:
                            lesson.google_event_id = google_event_id
                            lesson.last_synced_at = datetime.now(timezone.utc)
                            lesson.last_synced_content_hash = lesson_data.content_hash
                            session.commit()
                    except HttpError as error:
                        print(f"Не удалось создать событие в Google Calendar для {lesson_data.subject}: {error}")

    def sync_lesson(self, lesson: Lesson) -> None:
        """
        Sync a single lesson to Google Calendar (create or update).
        Used for initial sync or when a lesson is modified outside of ICS import.
        """
        try:
            service = get_google_calendar_service()
        except Exception as e:
            print(f"Не удалось пройти аутентификацию в Google Calendar: {e}")
            return

        with self.db.session() as session:
            lesson_db = session.query(Lesson).filter(Lesson.id == lesson.id).first()
            if not lesson_db:
                return

            event = _lesson_to_google_event(lesson_db)
            if lesson_db.google_event_id:
                try:
                    service.events().update(
                        calendarId=self.calendar_id,
                        eventId=lesson_db.google_event_id,
                        body=event,
                    ).execute()
                    # Update last_synced_at and last_synced_content_hash after successful update.
                    lesson_db.last_synced_at = datetime.now(timezone.utc)
                    lesson_db.last_synced_content_hash = lesson_db.content_hash
                    session.commit()
                except HttpError as error:
                    print(f"Не удалось обновить событие в Google Calendar для {lesson_db.subject}: {error}")
            else:
                try:
                    created_event = service.events().insert(calendarId=self.calendar_id, body=event).execute()
                    google_event_id = created_event.get("id")
                    print(f"Создано событие Google {created_event.get('id')} для {lesson_db.subject}")
                    lesson_db.google_event_id = google_event_id
                    lesson_db.last_synced_at = datetime.now(timezone.utc)
                    lesson_db.last_synced_content_hash = lesson_db.content_hash
                    session.commit()
                except HttpError as error:
                    print(f"Не удалось создать событие в Google Calendar для {lesson_db.subject}: {error}")