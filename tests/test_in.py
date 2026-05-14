from datetime import date

from nldate import parse


def test_in_three_months():
    assert parse(
        "in 3 months",
        today=date(2025, 1, 1)
    ) == date(2025, 4, 1)


def test_in_one_year():
    assert parse(
        "in 1 year",
        today=date(2025, 1, 1)
    ) == date(2026, 1, 1)

def test_in_five_days():
    assert parse(
        "in 5 days",
        today=date(2025, 1, 1)
    ) == date(2025, 1, 6)