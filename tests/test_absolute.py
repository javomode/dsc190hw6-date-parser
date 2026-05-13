from datetime import date

from nldate import parse


def test_iso_date():
    assert parse("2025-12-25") == date(2025, 12, 25)


def test_written_date():
    assert parse("December 25, 2025") == date(2025, 12, 25)