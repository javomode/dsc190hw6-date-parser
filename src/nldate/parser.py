import re
from datetime import date, timedelta

from dateutil.parser import parse as dateutil_parse


NUMBER_WORDS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

UNITS = {
    "day": "days",
    "days": "days",
    "week": "weeks",
    "weeks": "weeks",
}

DIRECTIONS = {
    "ago": -1,
    "before": -1,
    "after": 1,
    "later": 1,
}


def normalize_input(s: str) -> list[str]:
    """
    Lowercase, remove punctuation, and split input into tokens.
    """

    cleaned = re.sub(r"[,\s]+", " ", s.lower().strip())

    return cleaned.split()


def parse_number(token: str) -> int:
    """
    Convert numeric words into integers.
    """

    if token.isdigit():
        return int(token)

    if token in NUMBER_WORDS:
        return NUMBER_WORDS[token]

    raise ValueError(f"Unknown number: {token}")


def build_delta(quantity: int, unit: str) -> timedelta:
    """
    Convert quantity + unit into timedelta.
    """

    if unit not in UNITS:
        raise ValueError(f"Unsupported unit: {unit}")

    normalized_unit = UNITS[unit]

    if normalized_unit == "days":
        return timedelta(days=quantity)

    if normalized_unit == "weeks":
        return timedelta(weeks=quantity)

    raise ValueError(f"Unsupported unit type: {unit}")


def parse_relative_expression(tokens: list[str], today: date) -> date:
    """
    Handle:
    - 3 days ago
    - a week later
    """

    quantity = parse_number(tokens[0])

    unit = tokens[1]

    direction = tokens[2]

    if direction not in DIRECTIONS:
        raise ValueError(f"Unsupported direction: {direction}")

    multiplier = DIRECTIONS[direction]

    delta = build_delta(quantity, unit)

    return today + (multiplier * delta)


def parse_in_expression(tokens: list[str], today: date) -> date:
    """
    Handle:
    - in 3 days
    - in two weeks
    """

    quantity = parse_number(tokens[1])

    unit = tokens[2]

    delta = build_delta(quantity, unit)

    return today + delta


def parse_next_expression(tokens: list[str], today: date) -> date:
    """
    Handle:
    - next day
    - next week
    """

    unit = tokens[1]

    delta = build_delta(1, unit)

    return today + delta


def parse_complex_expression(tokens: list[str]) -> date:
    """
    Handle:
    - 5 days before December 1st 2025
    - 2 weeks after January 1st 2026
    """

    quantity = parse_number(tokens[0])

    unit = tokens[1]

    direction = tokens[2]

    if direction not in {"before", "after"}:
        raise ValueError("Invalid complex expression direction")

    base_date_string = " ".join(tokens[3:])

    base_date = dateutil_parse(base_date_string).date()

    delta = build_delta(quantity, unit)

    if direction == "before":
        return base_date - delta

    return base_date + delta


def parse_absolute_date(s: str) -> date:
    """
    Parse:
    - 2025-12-25
    - December 25 2025
    """

    return dateutil_parse(s).date()


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    tokens = normalize_input(s)

    # Simple keywords
    if tokens == ["today"]:
        return today

    if tokens == ["tomorrow"]:
        return today + timedelta(days=1)

    if tokens == ["yesterday"]:
        return today - timedelta(days=1)

    # in X days
    if (
        len(tokens) == 3
        and tokens[0] == "in"
        and tokens[2] in UNITS
    ):
        return parse_in_expression(tokens, today)

    # next week/day
    if (
        len(tokens) == 2
        and tokens[0] == "next"
        and tokens[1] in UNITS
    ):
        return parse_next_expression(tokens, today)

    # X days ago
    if (
        len(tokens) == 3
        and tokens[1] in UNITS
        and tokens[2] in DIRECTIONS
    ):
        return parse_relative_expression(tokens, today)

    # X days before DATE
    if (
        len(tokens) >= 4
        and tokens[1] in UNITS
        and tokens[2] in {"before", "after"}
    ):
        return parse_complex_expression(tokens)

    # absolute date fallback
    try:
        return parse_absolute_date(s)

    except ValueError:
        pass

    raise ValueError(f"Unsupported date format: {s}")