import os
import sqlite3

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Замените на путь к вашему модулю, где лежат get_credentials_path / get_token_path
from app.google_calendar.auth import get_credentials_path, get_token_path

# --- НАСТРОЙКИ ---
DB_PATH = os.getenv("XO_OS_DB_PATH", "data/xo_os.db")
print(DB_PATH)
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Укажите ID календарей, из которых нужно удалять.
CALENDARS_TO_CLEAN = [
    "primary",
    "2f683e4340a3f4e7822777af3df4479af5d25f22826f3c306d1d8d6999b7682f@group.calendar.google.com",
]


def get_calendar_service():
    """Возвращает авторизованный сервис Google Calendar."""
    creds = None
    token_path = get_token_path()
    creds_path = get_credentials_path()

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Сохраняем обновлённый токен
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def get_event_ids_from_db(db_path: str) -> list[str]:
    """Достаёт все непустые google_event_id из таблицы lessons."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT google_event_id
            FROM lessons
            WHERE google_event_id IS NOT NULL
              AND google_event_id != ''
            """
        )
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def _delete_callback(request_id, response, exception):
    if exception:
        # 404 = событие уже удалено или его нет в этом календаре — не считаем критичным
        print(f"  ! Ошибка при удалении {request_id}: {exception}")
    else:
        print(f"  + Удалено {request_id}")


def clear_calendar(service, calendar_id: str, event_ids: list[str]) -> None:
    """Пакетно удаляет события из указанного календаря."""
    print(f"\n--- Очистка календаря: {calendar_id} ---")

    chunk_size = 1000  # Google принимает до 1000 запросов в одном batch
    for i in range(0, len(event_ids), chunk_size):
        chunk = event_ids[i : i + chunk_size]
        batch = service.new_batch_http_request(callback=_delete_callback)

        for event_id in chunk:
            batch.add(service.events().delete(calendarId=calendar_id, eventId=event_id))

        print(f"  Отправка пакета из {len(chunk)} событий...")
        batch.execute()
        print("  Пакет обработан.")


def main():
    service = get_calendar_service()
    event_ids = get_event_ids_from_db(DB_PATH)

    print(f"Найдено {len(event_ids)} событий для удаления.")

    if not event_ids:
        print("Нечего удалять.")
        return

    for calendar_id in CALENDARS_TO_CLEAN:
        clear_calendar(service, calendar_id, event_ids)

    print("\nГотово!")


if __name__ == "__main__":
    main()
