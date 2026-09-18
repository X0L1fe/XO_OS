from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from app.database.db import Database
from app.database.models import User
from app.sync.service import SyncService


def cmd_status(db: Database) -> int:
    """Show current application status."""
    print("XO_OS status")
    print(f"Database: {db.url}")

    try:
        with db.session() as session:
            from app.database.models import Lesson, User, UserStats

            users = session.query(User).count()
            lessons = session.query(Lesson).count()
            stats = session.query(UserStats).count()

            print(f"Users: {users}")
            print(f"Lessons: {lessons}")
            print(f"UserStats: {stats}")

        return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def cmd_import_ics(
    db: Database,
    file_path: str,
    *,
    calendar: str | None = None,
    user_id: int,
) -> int:
    """Import an ICS file and optionally sync it to Google Calendar."""

    with db.session() as session:
        user = session.query(User).filter(User.id == user_id).first()

    if user is None:
        print(
            f"User with ID {user_id} not found.",
            file=sys.stderr,
        )

    path = Path(file_path)

    if not path.is_file():
        print(
            f"File not found: {path}",
            file=sys.stderr,
        )
        return 1

    try:
        content = path.read_bytes()

        google_calendar_service = None

        # Подключаем Google Calendar, если указан календарь
        # и интеграция доступна.
        if calendar:
            try:
                from app.google_calendar.service import (
                    GoogleCalendarSyncService,
                )

                google_calendar_service = GoogleCalendarSyncService(
                    db,
                    calendar_name=calendar,
                    user_id=user_id,
                )

            except Exception as exc:
                print(
                    f"Google Calendar initialization failed: {exc}",
                    file=sys.stderr,
                )
                return 1

        service = SyncService(
            db,
            google_calendar_service=google_calendar_service,
        )

        result = service.import_ics(
            content,
            user_id=user_id,
        )
        print(f"Parsed:    {result.parsed}")
        print(f"Created:   {result.created}")
        print(f"Updated:   {result.updated}")
        print(f"Moved:     {result.moved}")
        print(f"Deleted:   {result.deleted}")
        print(f"Unchanged: {result.unchanged}")

        if calendar:
            print(f"Calendar:  {calendar}")

        return 0

    except Exception as exc:
        print(
            f"Import failed: {exc}",
            file=sys.stderr,
        )
        return 1


def cmd_export(db: Database, vault: str) -> int:
    """Export lessons to Obsidian."""
    try:
        exported = SyncService(db).export_to_obsidian(vault)

        print(f"Exported lessons: {exported}")
        print(f"Vault: {vault}")

        return 0

    except Exception as exc:
        print(f"Export failed: {exc}", file=sys.stderr)
        return 1


def cmd_stats(db: Database) -> int:
    """Show user statistics."""
    try:
        from app.database.models import UserStats

        with db.session() as session:
            stats = session.query(UserStats).order_by(UserStats.id).first()

            if stats is None:
                print("No statistics found.")
                return 0

            print(f"Level:           {stats.level}")
            print(f"Total XP:        {stats.total_xp}")
            print(f"Current streak:  {stats.current_streak}")
            print(f"Max streak:      {stats.max_streak}")
            print(f"Last activity:   {stats.last_activity_date}")

        return 0

    except Exception as exc:
        print(f"Stats failed: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xo-os",
        description="XO_OS command line interface",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # ========================================================
    # STATUS
    # ========================================================

    subparsers.add_parser(
        "status",
        help="Show application status",
    )

    # ========================================================
    # IMPORT
    # ========================================================

    import_parser = subparsers.add_parser(
        "import",
        help="Import an ICS file",
    )

    import_parser.add_argument(
        "--calendar",
        default=os.getenv(
            "GOOGLE_CALENDAR_NAME",
            None,
        ),
        help="Google Calendar name",
    )

    import_parser.add_argument(
        "--user-id",
        type=int,
        required=True,
        help="XO_OS user ID",
    )

    import_parser.add_argument(
        "file",
        help="Path to ICS file",
    )

    # ========================================================
    # EXPORT
    # ========================================================

    export_parser = subparsers.add_parser(
        "export",
        help="Export lessons to Obsidian",
    )

    export_parser.add_argument(
        "vault",
        help="Path to Obsidian vault",
    )

    # ========================================================
    # STATS
    # ========================================================

    subparsers.add_parser(
        "stats",
        help="Show user statistics",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    db = Database()

    if args.command == "status":
        return cmd_status(db)

    if args.command == "import":
        return cmd_import_ics(
            db,
            args.file,
            calendar=args.calendar,
            user_id=args.user_id,
        )

    if args.command == "export":
        return cmd_export(
            db,
            args.vault,
        )

    if args.command == "stats":
        return cmd_stats(db)

    parser.error(f"Unknown command: {args.command}")

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
