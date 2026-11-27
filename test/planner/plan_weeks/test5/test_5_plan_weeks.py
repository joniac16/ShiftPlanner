"""Unit test 5 for library.planner.plan_weeks: the start week is after the end week.

Asking for 2027-W6 to 2027-W5 raises DataError; nothing is planned.
"""

from pathlib import Path

import pytest

from library.loader import DataError
from library.planner import plan_weeks

DATA_DIR = Path(__file__).parent / "data"
HISTORY = DATA_DIR / "history"


def test_5_plan_weeks():
    with pytest.raises(DataError, match="The start week 2027-W6 is after the end week 2027-W5") as error:
        plan_weeks(2027, 6, 2027, 5, data_dir=DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")
