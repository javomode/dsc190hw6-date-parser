from datetime import date

from nldate import parse


def test_days_ago():
    assert parse("3 days ago", today=date(2025, 1, 10)) == date(2025, 1, 7)


def test_week_later():
    assert parse("a week later", today=date(2025, 1, 1)) == date(2025, 1, 8)


def test_two_weeks_after():
    assert parse("two weeks after", today=date(2025, 1, 1)) == date(2025, 1, 15)


def test_one_day_before():
    assert parse("1 day before", today=date(2025, 1, 10)) == date(2025, 1, 9)
