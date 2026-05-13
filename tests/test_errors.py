import pytest
from datetime import date

from nldate import parse


def test_invalid_number():
    with pytest.raises(ValueError):
        parse("hundred days ago", today=date(2025, 1, 1))


def test_invalid_unit():
    with pytest.raises(ValueError):
        parse("3 bananas ago", today=date(2025, 1, 1))


def test_invalid_direction():
    with pytest.raises(ValueError):
        parse("3 days sideways", today=date(2025, 1, 1))


def test_unknown_expression():
    with pytest.raises(ValueError):
        parse("purple elephant", today=date(2025, 1, 1))