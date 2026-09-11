from pathlib import Path

from app.ics.parser import parse_ics


WEEK_FILE = Path(
    "timetable_М3О-210БВ-25_week_1.ics"
)

SEMESTER_FILE = Path(
    "timetable_М3О-210БВ-25_semester.ics"
)


def test_week_filters_military():
    """
    В исходном недельном ICS 18 событий.

    4 относятся к военной подготовке.

    Для текущего профиля остаётся 14.
    """
    lessons = parse_ics(
        WEEK_FILE.read_bytes()
    )

    assert len(lessons) == 14

    assert all(
        lesson.category != "MILITARY"
        for lesson in lessons
    )


def test_week_can_include_military():
    """
    Проверяем, что parser всё-таки умеет
    работать с другим профилем.
    """
    lessons = parse_ics(
        WEEK_FILE.read_bytes(),
        include_military=True,
    )

    assert len(lessons) == 18

    assert sum(
        lesson.category == "MILITARY"
        for lesson in lessons
    ) == 4


def test_semester_filters_military():
    """
    В семестровом файле 328 событий.

    Военная подготовка + связанные элективы
    не должны попасть в текущий профиль.
    """
    lessons = parse_ics(
        SEMESTER_FILE.read_bytes()
    )

    assert all(
        lesson.category != "MILITARY"
        for lesson in lessons
    )


def test_lecture_parsing():
    lessons = parse_ics(
        WEEK_FILE.read_bytes()
    )

    lesson = next(
        lesson
        for lesson in lessons
        if lesson.subject == "Теория графов"
    )

    assert lesson.lesson_type == "LECTURE"

    assert lesson.teachers == (
        "ЕГОРОВА ЕВГЕНИЯ КИРИЛЛОВНА",
    )

    assert lesson.room == "ГУК В-214"

    assert (
        lesson.start_time.isoformat()
        == "2026-09-05T13:00:00+03:00"
    )


def test_lab_multiple_teachers():
    lessons = parse_ics(
        SEMESTER_FILE.read_bytes()
    )

    lesson = next(
        lesson
        for lesson in lessons
        if (
            lesson.subject
            == "Метрология и стандартизация"
            and lesson.lesson_type == "LAB"
        )
    )

    assert lesson.teachers == (
        "Бурова Аделия Юрьевна",
        "Версин Александр Андреевич",
    )


def test_week_and_semester_have_different_source_uid():
    """
    МАИ создаёт разные UID для одного и того же занятия
    в недельном и семестровом экспорте.
    """
    week = parse_ics(
        WEEK_FILE.read_bytes()
    )

    semester = parse_ics(
        SEMESTER_FILE.read_bytes()
    )

    week_lesson = next(
        lesson
        for lesson in week
        if (
            lesson.subject == "Теория графов"
            and lesson.start_time.strftime(
                "%Y-%m-%d %H:%M"
            )
            == "2026-09-05 13:00"
        )
    )

    semester_lesson = next(
        lesson
        for lesson in semester
        if (
            lesson.subject == "Теория графов"
            and lesson.start_time.strftime(
                "%Y-%m-%d %H:%M"
            )
            == "2026-09-05 13:00"
        )
    )

    assert (
        week_lesson.source_uid
        != semester_lesson.source_uid
    )

    assert (
        week_lesson.identity_key
        == semester_lesson.identity_key
    )