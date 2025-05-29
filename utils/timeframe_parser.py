import re

def parse_natural_timeframe(user_input: str) -> str:
    user_input = user_input.lower().strip()

    mappings = {
        "today": "1d",
        "yesterday": "2d",
        "this week": "5d",
        "last week": "10d",
        "last month": "1mo",
        "last 3 months": "3mo",
        "last quarter": "3mo",
        "last 6 months": "6mo",
        "half year": "6mo",
        "last year": "1y",
        "past year": "1y",
        "this year": "ytd",
        "max": "max"
    }

    if user_input in mappings:
        return mappings[user_input]

    match = re.match(r"(?:last\s*)?(\d+)\s*(day|week|month|year|y|d|w|mo)s?", user_input)
    if match:
        num, unit = match.groups()
        unit = unit.lower()
        abbrev = {
            "day": "d", "d": "d",
            "week": "wk", "w": "wk",
            "month": "mo", "mo": "mo",
            "year": "y", "y": "y"
        }.get(unit, "")
        return f"{num}{abbrev}"

    return "1mo"