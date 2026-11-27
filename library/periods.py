"""Helpers for planning periods expressed as ISO weeks, e.g. "2026-W48"."""

from datetime import date, timedelta


def parse_period(period: str) -> date:
    """Return the Monday of the given ISO week ("2026-W48" -> 2026-11-23)."""
    year, week = period.split("-W")
    return date.fromisocalendar(int(year), int(week), 1)


def format_period(day: date) -> str:
    """Return the ISO week that contains the given date (2026-11-23 -> "2026-W48")."""
    year, week, _ = day.isocalendar()
    return f"{year}-W{week:02d}"


def next_period(period: str, weeks: int = 1) -> str:
    """Move a period forward (or backward, with a negative value) by a number of weeks."""
    return format_period(parse_period(period) + timedelta(weeks=weeks))


def weeks_between(start: str, end: str) -> int:
    """Number of weeks from start to end (negative if end is before start)."""
    return (parse_period(end) - parse_period(start)).days // 7
