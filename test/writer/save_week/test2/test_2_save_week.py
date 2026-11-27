"""Unit test 2 for library.writer.save_week: an invalid week raises DataError and writes nothing.

Dummy data: L1 Morning needs 1 qualified and 1 assistant in 2027-W5.
  OP1 qualified on L1, OP2 no training; both available in the morning.
  History: 2027-W4.

The allocation puts OP2 (no training) in a qualified slot, so validate_week
fails and no file is created.
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
    Assignment(operator="OP2", line="L1", shift="Morning", role="qualified"),
])

EXPECTED_TEXT = """{
  "period": "2027-W5",
  "assignments": [
    {"operator": "OP1", "line": "L1", "shift": "Morning", "role": "qualified"},
    {"operator": "OP2", "line": "L1", "shift": "Morning", "role": "assistant"}
  ]
}
"""


def test_2_save_week():
    with pytest.raises(DataError, match=r"OP2 \(no training on L1\) cannot take a qualified slot") as error:
        save_week(ALLOCATION, DATA_DIR)

    print(f"\nDataError raised as expected: {error.value}")

    assert not TARGET.exists()
