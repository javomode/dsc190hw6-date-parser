from datetime import date

from nldate import parse


def test_tomorrow():
    assert parse("tomorrow", today=date(2025, 1, 1)) == date(2025, 1, 2)