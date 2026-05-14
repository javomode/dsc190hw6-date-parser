from datetime import date

from nldate import parse


def test_day_after_tomorrow():
    assert parse(
        "the day after tomorrow",
        today=date(2025, 1, 1)
    ) == date(2025, 1, 3)


def test_day_before_yesterday():
    assert parse(
        "the day before yesterday",
        today=date(2025, 1, 1)
    ) == date(2024, 12, 30)


def test_day_after_tomorrow_default_today():
    # just ensures no crash without explicit today override
    result = parse("the day after tomorrow")
    assert isinstance(result, date)


def test_special_phrase_with_different_today():
    assert parse(
        "the day after tomorrow",
        today=date(2024, 12, 31)
    ) == date(2025, 1, 2)


def test_day_after_tomorrow_with_extra_spaces():
    assert parse(
        "the   day   after   tomorrow",
        today=date(2025, 1, 1)
    ) == date(2025, 1, 3)