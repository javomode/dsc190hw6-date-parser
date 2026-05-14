from datetime import date

from nldate import parse


def test_five_days_ago():
    assert parse("five days ago", today=date(2025, 1, 10)) == date(2025, 1, 5)


def test_ten_weeks_after():
    assert parse("ten weeks after", today=date(2025, 1, 1)) == date(2025, 3, 12)


def test_in_three_days():
    assert parse("in 3 days", today=date(2025, 1, 1)) == date(2025, 1, 4)


def test_in_two_weeks():
    assert parse("in two weeks", today=date(2025, 1, 1)) == date(2025, 1, 15)


def test_next_week():
    assert parse("next week", today=date(2025, 1, 1)) == date(2025, 1, 8)


def test_next_day():
    assert parse("next day", today=date(2025, 1, 1)) == date(2025, 1, 2)


def test_next_tuesday():
    # assume today is Monday
    assert parse(
        "next tuesday",
        today=date(2025, 1, 6),  # Monday
    ) == date(2025, 1, 7)


def test_next_tuesday_wrap():
    # if today is Tuesday, next Tuesday is 7 days later
    assert parse(
        "next tuesday",
        today=date(2025, 1, 7),  # Tuesday
    ) == date(2025, 1, 14)


def test_next_tuesday_midweek():
    assert parse(
        "next tuesday",
        today=date(2025, 1, 8),  # Wednesday
    ) == date(2025, 1, 14)


def test_last_friday():
    # Saturday Jan 10 2026 → last Friday is Jan 9 2026
    assert parse("last friday", today=date(2026, 1, 10)) == date(2026, 1, 9)


def test_last_friday_same_week():
    # Friday itself → last Friday is 7 days earlier
    assert parse("last friday", today=date(2026, 1, 9)) == date(2026, 1, 2)


def test_last_friday_midweek():
    assert parse(
        "last friday",
        today=date(2026, 1, 14),  # Wednesday
    ) == date(2026, 1, 9)
