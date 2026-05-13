from datetime import date

import pytest

from nldate import parse


def test_complex1():
    assert parse("5 days before December 1st, 2025") == date(2025, 11, 26)


def test_complex2():
    assert parse("10 days after January 1st, 2025") == date(2025, 1, 11)


def test_complex_word_number():
    assert parse("five days after January 1st, 2025") == date(2025, 1, 6)


def test_complex_punctuation():
    assert parse("5 days before December 1st 2025") == date(2025, 11, 26)


def test_complex_formatting():
    assert parse("   5 DAYS BEFORE   December 1st, 2025   ") == date(2025, 11, 26)


def test_complex_invalid_unit():
    with pytest.raises(ValueError):
        parse("5 bananas before December 1st, 2025")
