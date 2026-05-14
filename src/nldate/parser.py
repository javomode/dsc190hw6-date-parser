import re
from datetime import date, timedelta

from dateutil.parser import parse as dateutil_parse
from dateutil.relativedelta import relativedelta

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
    "month": "months",
    "months": "months",
    "year": "years",
    "years": "years",
}

DIRECTIONS = {
    "ago": -1,
    "before": -1,
    "after": 1,
    "later": 1,
}

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
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


def build_delta(quantity: int, unit: str) -> timedelta | relativedelta:
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

    if normalized_unit == "months":
        return relativedelta(months=quantity)

    if normalized_unit == "years":
        return relativedelta(years=quantity)

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


def parse_next_weekday(tokens: list[str], today: date) -> date:
    """
    Handle:
    - next Monday/Tuesday/...
    """
    weekday_name = tokens[1]
    target = WEEKDAYS[weekday_name]

    current = today.weekday()

    days_ahead = target - current

    if days_ahead <= 0:
        days_ahead += 7

    return today + timedelta(days=days_ahead)


def parse_from_now_expression(tokens: list[str], today: date) -> date:
    """
    Handle:
    - 5 days from now
    - 3 months from now
    """
    quantity = parse_number(tokens[0])
    unit = tokens[1]

    delta = build_delta(quantity, unit)

    return today + delta


def parse_last_weekday(tokens: list[str], today: date) -> date:
    """
    Handle:
    - last Monday/Tuesday/...
    """
    weekday_name = tokens[1]
    target = WEEKDAYS[weekday_name]

    current = today.weekday()

    days_behind = current - target

    if days_behind <= 0:
        days_behind += 7

    return today - timedelta(days=days_behind)


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


def parse_compound_expression(tokens: list[str]) -> date:
    """
    Handle:
    - 2 years, 3 months before Dec 1 2025
    - 1 year 2 months after Jan 1 2020
    """

    # find direction index
    if "before" in tokens:
        direction = -1
        split_idx = tokens.index("before")
    elif "after" in tokens:
        direction = 1
        split_idx = tokens.index("after")
    else:
        raise ValueError("Missing before/after")

    # left side = offsets
    offset_tokens = tokens[:split_idx]
    base_tokens = tokens[split_idx + 1 :]

    base_date = dateutil_parse(" ".join(base_tokens)).date()

    delta = relativedelta()

    i = 0
    while i < len(offset_tokens):
        quantity = parse_number(offset_tokens[i])
        unit = offset_tokens[i + 1]

        normalized = UNITS[unit]

        if normalized == "days":
            delta += relativedelta(days=quantity)
        elif normalized == "weeks":
            delta += relativedelta(weeks=quantity)
        elif normalized == "months":
            delta += relativedelta(months=quantity)
        elif normalized == "years":
            delta += relativedelta(years=quantity)

        i += 2

    if direction == -1:
        return base_date - delta
    else:
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
    if len(tokens) == 3 and tokens[0] == "in" and tokens[2] in UNITS:
        return parse_in_expression(tokens, today)

    # next Tuesday
    if len(tokens) == 2 and tokens[0] == "next" and tokens[1] in WEEKDAYS:
        return parse_next_weekday(tokens, today)

    # next week/day
    if len(tokens) == 2 and tokens[0] == "next" and tokens[1] in UNITS:
        return parse_next_expression(tokens, today)

    # last Friday
    if len(tokens) == 2 and tokens[0] == "last" and tokens[1] in WEEKDAYS:
        return parse_last_weekday(tokens, today)

    # X days ago
    if len(tokens) == 3 and tokens[1] in UNITS and tokens[2] in DIRECTIONS:
        return parse_relative_expression(tokens, today)

    # X weeks from now
    if (
        len(tokens) == 4
        and tokens[2] == "from"
        and tokens[3] == "now"
        and tokens[1] in UNITS
    ):
        return parse_from_now_expression(tokens, today)

    # compound offsets: 2 years, 3 months before DATE
    if any(token in {"before", "after"} for token in tokens):
        # must contain at least TWO unit patterns to be "compound"
        unit_count = sum(token in UNITS for token in tokens)
        if unit_count >= 2:
            return parse_compound_expression(tokens)

    # X days before DATE
    if len(tokens) >= 4 and tokens[1] in UNITS and tokens[2] in {"before", "after"}:
        return parse_complex_expression(tokens)

    # absolute date fallback
    try:
        return parse_absolute_date(s)

    except ValueError:
        pass

    raise ValueError(f"Unsupported date format: {s}")
