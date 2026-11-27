"""Small helper functions used across the project.

Planning periods are ISO weeks written as "<year>-W<week>", with no leading
zero ("2027-W5", "2027-W12"). They are used as keys in demands.json and
availabilities.json and as file names in data/output and data/history.
"""

from datetime import date


def iso_week_to_date(iso_week: str) -> date:
    """Return the Monday of an ISO week: "2027-W5" -> date(2027, 2, 1).

    Raises ValueError if the text is not a valid ISO week (e.g. "2027-W53",
    since 2027 only has 52 weeks).
    """
    year, week = iso_week.split("-W")
    return date.fromisocalendar(int(year), int(week), 1)


def sort_iso_weeks(iso_weeks: list[str]) -> list[str]:
    """Return the ISO weeks sorted chronologically.

    Sorting them as text would be wrong without leading zeros
    ("2027-W10" would come before "2027-W2").
    """
    return sorted(iso_weeks, key=iso_week_to_date)
