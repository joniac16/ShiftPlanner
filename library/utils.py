"""Small helper functions used across the project.

Planning periods are ISO weeks written as "<year>-W<week>", with no leading
zero ("2027-W5", "2027-W12"). They are used as keys in demands.json and
availabilities.json and as file names in data/history.
"""

import shutil
from datetime import date, timedelta
from pathlib import Path

SAMPLE_DATA_DIR = Path("sample_data")


def ensure_data_dir(data_dir: Path | str, sample_dir: Path | str = SAMPLE_DATA_DIR) -> bool:
    """Make sure the working data folder has data: if `data_dir/source` does
    not exist, copy the sample data (`sample_data/`: source/ and history/)
    into `data_dir`. Returns True if it copied the sample data, False if the
    folder already had data.

    The working folder (`data/` by default) is ignored by git, so planning or
    editing data there never changes the repository. To start again from the
    sample data, delete its contents.
    """
    data_dir, sample_dir = Path(data_dir), Path(sample_dir)
    if (data_dir / "source").exists():
        return False
    shutil.copytree(sample_dir, data_dir, dirs_exist_ok=True)
    return True


def make_iso_week(year: int, week: int) -> str:
    """Build an ISO week text from its year and week number: (2027, 5) -> "2027-W5".

    Raises ValueError if the week does not exist (e.g. week 53 of 2027).
    """
    date.fromisocalendar(year, week, 1)  # validates
    return f"{year}-W{week}"


def next_iso_week(iso_week: str) -> str:
    """Return the following ISO week: "2027-W5" -> "2027-W6", "2026-W53" -> "2027-W1"."""
    year, week, _ = (iso_week_to_date(iso_week) + timedelta(weeks=1)).isocalendar()
    return f"{year}-W{week}"


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
