from datetime import date

import pytest

from nldate import parse


def test_from_now_weeks():
    assert parse("2 weeks from now", today=date(2025, 1, 1)) == date(2025, 1, 15)


def test_from_now_single():
    assert parse("1 day from now", today=date(2025, 1, 1)) == date(2025, 1, 2)


def test_from_now_months():
    assert parse("3 months from now", today=date(2025, 1, 1)) == date(2025, 4, 1)


def test_from_now_invalid():
    with pytest.raises(ValueError):
        parse("2 bananas from now")
