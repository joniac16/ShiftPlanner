"""Unit test 3 for library.writer.save_week: a week already in the history is not overwritten.

Dummy data: L1 Morning needs 1 qualified and 1 assistant in 2027-W5.
  OP1 qualified on L1, OP2 no training; both available in the morning.
  History: 2027-W4.
  data/history/2027-W5.json already exists (part of the dummy data).

Without overwrite=True, save_week raises DataError and the existing file is
left unchanged.
"""

from pathlib import Path

import pytest

from library.loader import DataError
from library.models import Assignment, WeekAllocation
from library.writer import save_week

DATA_DIR = Path(__file__).parent / "data"
TARGET = DATA_DIR / "history" / "2027-W5.json"

ALLOCATION = WeekAllocation(period="2027-W5", assignments=[
    Assignment(operator="OP1", line="L1", shift="Morning", role="qualified"),
    Assignment(operator="OP2", line="L1", shift="Morning", role="assistant"),
])

EXPECTED_TEXT = """{
  "period": "2027-W5",
  "assignments": [
    {"operator": "OP1", "line": "L1", "shift": "Morning", "role": "qualified"},
    {"operator": "OP2", "line": "L1", "shift": "Morning", "role": "assistant"}
  ]
}
"""


def test_3_save_week():
    before = TARGET.read_text()

    with pytest.raises(DataError, match="Week 2027-W5 is already in the history") as error:
        save_week(ALLOCATION, DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")

    assert TARGET.read_text() == before
