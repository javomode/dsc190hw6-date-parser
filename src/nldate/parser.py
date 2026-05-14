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
    cleaned = re.sub(r"[,\s]+", " ", s.lower().strip())
    return cleaned.split()


def parse_number(token: str) -> int:
    if token.isdigit():
        return int(token)
    if token in NUMBER_WORDS:
        return NUMBER_WORDS[token]
    raise ValueError(f"Unknown number: {token}")


def build_delta(quantity: int, unit: str) -> relativedelta:
    if unit not in UNITS:
        raise ValueError(f"Unsupported unit: {unit}")

    normalized = UNITS[unit]

    if normalized == "days":
        return relativedelta(days=quantity)
    if normalized == "weeks":
        return relativedelta(weeks=quantity)
    if normalized == "months":
        return relativedelta(months=quantity)
    if normalized == "years":
        return relativedelta(years=quantity)

    raise ValueError(f"Unsupported unit: {unit}")


def parse_base_date(tokens: list[str], today: date) -> date:
    if tokens == ["today"]:
        return today
    if tokens == ["tomorrow"]:
        return today + timedelta(days=1)
    if tokens == ["yesterday"]:
        return today - timedelta(days=1)

    if len(tokens) == 2:
        if tokens[0] == "next" and tokens[1] in WEEKDAYS:
            return parse_next_weekday(tokens, today)
        if tokens[0] == "last" and tokens[1] in WEEKDAYS:
            return parse_last_weekday(tokens, today)

    try:
        return dateutil_parse(" ".join(tokens), fuzzy=False).date()
    except Exception:
        raise ValueError(f"Unsupported base date: {' '.join(tokens)}")


def parse_relative_expression(tokens: list[str], today: date) -> date:
    quantity = parse_number(tokens[0])
    unit = tokens[1]
    direction = tokens[2]

    if direction not in DIRECTIONS:
        raise ValueError(f"Unsupported direction: {direction}")

    delta = build_delta(quantity, unit)
    return today + DIRECTIONS[direction] * delta


def parse_in_expression(tokens: list[str], today: date) -> date:
    quantity = parse_number(tokens[1])
    unit = tokens[2]
    delta = build_delta(quantity, unit)
    return today + delta


def parse_next_expression(tokens: list[str], today: date) -> date:
    unit = tokens[1]
    delta = build_delta(1, unit)
    return today + delta


def parse_next_weekday(tokens: list[str], today: date) -> date:
    weekday_name = tokens[1]
    target = WEEKDAYS[weekday_name]

    current = today.weekday()
    days_ahead = target - current

    if days_ahead <= 0:
        days_ahead += 7

    return today + timedelta(days=days_ahead)


def parse_from_now_expression(tokens: list[str], today: date) -> date:
    quantity = parse_number(tokens[0])
    unit = tokens[1]
    delta = build_delta(quantity, unit)
    return today + delta


def parse_last_weekday(tokens: list[str], today: date) -> date:
    weekday_name = tokens[1]
    target = WEEKDAYS[weekday_name]

    current = today.weekday()
    days_behind = (current - target) % 7
    if days_behind == 0:
        days_behind = 7

    return today - timedelta(days=days_behind)


def parse_complex_expression(tokens: list[str], today: date) -> date:
    quantity = parse_number(tokens[0])
    unit = tokens[1]
    direction = tokens[2]

    if direction not in {"before", "after"}:
        raise ValueError("Invalid complex expression direction")

    base_tokens = tokens[3:]
    base_date = parse_base_date(base_tokens, today)

    delta = build_delta(quantity, unit)

    return base_date - delta if direction == "before" else base_date + delta


def is_compound(tokens: list[str]) -> bool:
    unit_count = sum(1 for t in tokens if t in UNITS)
    return "and" in tokens or unit_count > 1


def parse_compound_expression(tokens: list[str], today: date) -> date:
    if "before" in tokens:
        direction = -1
        split_idx = tokens.index("before")
    elif "after" in tokens:
        direction = 1
        split_idx = tokens.index("after")
    else:
        raise ValueError("Missing before/after")

    offset_tokens = tokens[:split_idx]
    base_tokens = tokens[split_idx + 1 :]

    base_date = parse_base_date(base_tokens, today)

    years = months = weeks = days = 0

    i = 0
    while i < len(offset_tokens):
        if offset_tokens[i] == "and":
            i += 1
            continue

        quantity = parse_number(offset_tokens[i])
        unit = offset_tokens[i + 1]

        normalized = UNITS[unit]

        if normalized == "years":
            years += quantity
        elif normalized == "months":
            months += quantity
        elif normalized == "weeks":
            weeks += quantity
        elif normalized == "days":
            days += quantity

        i += 2

    delta = relativedelta(years=years, months=months, weeks=weeks, days=days)

    return base_date + delta if direction == 1 else base_date - delta


def parse_compound_relative_expression(tokens: list[str], today: date) -> date:
    if "before" in tokens:
        direction = -1
        split_idx = tokens.index("before")
    elif "after" in tokens:
        direction = 1
        split_idx = tokens.index("after")
    else:
        raise ValueError("Missing before/after")

    offset_tokens = tokens[:split_idx]
    base_tokens = tokens[split_idx + 1 :]

    base_date = parse_base_date(base_tokens, today)

    years = months = weeks = days = 0

    i = 0
    while i < len(offset_tokens):
        if offset_tokens[i] == "and":
            i += 1
            continue

        quantity = parse_number(offset_tokens[i])
        raw_unit = offset_tokens[i + 1]

        if raw_unit not in UNITS:
            raise ValueError(f"Unsupported unit: {raw_unit}")

        unit = UNITS[raw_unit]

        if unit == "years":
            years += quantity
        elif unit == "months":
            months += quantity
        elif unit == "weeks":
            weeks += quantity
        elif unit == "days":
            days += quantity

        i += 2

    delta = relativedelta(years=years, months=months, weeks=weeks, days=days)

    result = base_date + (delta if direction == 1 else -delta)

    return result


def parse_absolute_date(s: str) -> date:
    try:
        return dateutil_parse(s, fuzzy=False).date()
    except Exception:
        raise ValueError(f"Unsupported absolute date: {s}")


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    tokens = normalize_input(s)

    if tokens == ["today"]:
        return today
    if tokens == ["tomorrow"]:
        return today + timedelta(days=1)
    if tokens == ["yesterday"]:
        return today - timedelta(days=1)

    if len(tokens) == 3 and tokens[0] == "in" and tokens[2] in UNITS:
        return parse_in_expression(tokens, today)

    if len(tokens) == 2:
        if tokens[0] == "next" and tokens[1] in WEEKDAYS:
            return parse_next_weekday(tokens, today)
        if tokens[0] == "last" and tokens[1] in WEEKDAYS:
            return parse_last_weekday(tokens, today)
        if tokens[0] == "next" and tokens[1] in UNITS:
            return parse_next_expression(tokens, today)

    if len(tokens) == 3 and tokens[1] in UNITS and tokens[2] in DIRECTIONS:
        return parse_relative_expression(tokens, today)

    if (
        len(tokens) == 4
        and tokens[1] in UNITS
        and tokens[2] == "from"
        and tokens[3] == "now"
    ):
        return parse_from_now_expression(tokens, today)

    if "before" in tokens or "after" in tokens:
        if "before" in tokens:
            split_idx = tokens.index("before")
        else:
            split_idx = tokens.index("after")

        offset_tokens = tokens[:split_idx]
        base_tokens = tokens[split_idx + 1 :]

        base_is_simple = base_tokens in (["today"], ["tomorrow"], ["yesterday"])
        base_is_weekday = len(base_tokens) == (
            2 and base_tokens[0] in {"next", "last"} and base_tokens[1] in WEEKDAYS
        )

        compound = is_compound(offset_tokens)

        if compound and (base_is_simple or base_is_weekday):
            return parse_compound_relative_expression(tokens, today)

        if compound:
            return parse_compound_expression(tokens, today)

        if not compound and len(offset_tokens) == 2:
            return parse_complex_expression(tokens, today)

    try:
        return parse_absolute_date(s)
    except ValueError:
        pass

    raise ValueError(f"Unsupported date format: {s}")
