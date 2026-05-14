from datetime import date

from nldate import parse


def test_compound_1():
    assert parse("2 years, 3 months before Dec 1, 2025") == date(2023, 9, 1)


def test_compound_after():
    assert parse("1 year 2 months after Jan 1, 2020") == date(2021, 3, 1)


def test_compound_no_comma():
    assert parse("2 years 3 months before Dec 1 2025") == date(2023, 9, 1)
