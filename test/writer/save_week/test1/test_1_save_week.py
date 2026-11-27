"""Unit test 1 for library.writer.save_week: a valid week is saved to the history.

Dummy data: L1 Morning needs 1 qualified and 1 assistant in 2027-W5.
  OP1 qualified on L1, OP2 no training; both available in the morning.
  History: 2027-W4.

The test removes data/history/2027-W5.json first (so it always starts from
the same state), saves the week and checks the file: its exact text, and that
load_history reads it back. The file stays there afterwards so it can be
opened; it is listed in data/history/.gitignore, so it is not committed.
"""

from pathlib import Path


from library.loader import load_history
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


def test_1_save_week():
    TARGET.unlink(missing_ok=True)

    path = save_week(ALLOCATION, DATA_DIR)

    print(f"\nsave_week wrote {path.name}:\n{path.read_text()}")

    assert path == TARGET
    assert path.read_text() == EXPECTED_TEXT
    assert load_history(DATA_DIR)[-1] == ALLOCATION
