"""Unit test 4 for library.writer.save_week: overwrite=True replaces a week already in the history.

Dummy data: L1 Morning needs 1 qualified and 1 assistant in 2027-W5.
  OP1 qualified on L1, OP2 no training; both available in the morning.
  History: 2027-W4.

The test first writes an old version of data/history/2027-W5.json (only
OP1), then saves the new one (OP1 and OP2) with overwrite=True and checks
that the file now holds the new version. The file is listed in
data/history/.gitignore.
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

OLD_TEXT = """{
  "period": "2027-W5",
  "assignments": [
    {"operator": "OP1", "line": "L1", "shift": "Morning", "role": "qualified"}
  ]
}
"""


def test_4_save_week():
    TARGET.write_text(OLD_TEXT)

    path = save_week(ALLOCATION, DATA_DIR, overwrite=True)

    print(f"\nsave_week overwrote {path.name}:\n{path.read_text()}")

    assert path.read_text() == EXPECTED_TEXT
    assert load_history(DATA_DIR)[-1] == ALLOCATION
