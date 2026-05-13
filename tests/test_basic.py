from datetime import date

from nldate import parse


def test_today():
    assert parse("today", today=date(2025, 1, 1)) == date(2025, 1, 1)


def test_tomorrow():
    assert parse("tomorrow", today=date(2025, 1, 1)) == date(2025, 1, 2)


def test_yesterday():
    assert parse("yesterday", today=date(2025, 1, 1)) == date(2024, 12, 31)
