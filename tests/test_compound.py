from datetime import date

from nldate import parse


def test_compound_1():
    assert parse("2 years, 3 months before Dec 1, 2025") == date(2023, 9, 1)


def test_compound_after():
    assert parse("1 year 2 months after Jan 1, 2020") == date(2021, 3, 1)


def test_compound_no_comma():
    assert parse("2 years 3 months before Dec 1 2025") == date(2023, 9, 1)


def test_compound_relative_1():
    assert parse("1 year and 2 months after yesterday", today=date(2025, 1, 1)) == date(
        2026, 2, 28
    )


def test_compound_relative_before():
    assert parse("1 year and 2 months before tomorrow", today=date(2025, 1, 1)) == date(
        2023, 11, 2
    )


def test_single_relative_base():
    assert parse("1 month after yesterday", today=date(2025, 1, 1)) == date(2025, 1, 31)
