"""Unit test 5 for library.writer.save_week: later weeks in the history: warning, saved anyway.

Dummy data: L1 Morning needs 1 qualified and 1 assistant in 2027-W5.
  OP1 qualified on L1, OP2 no training; both available in the morning.
  History: 2027-W4.
  data/history/2027-W6.json already exists (part of the dummy data).

Saving 2027-W5 prints a warning, because 2027-W6 was planned with the
previous version of 2027-W5, and saves the week anyway. The new file is
listed in data/history/.gitignore.
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


def test_5_save_week(capsys):
    TARGET.unlink(missing_ok=True)

    path = save_week(ALLOCATION, DATA_DIR)
    printed = capsys.readouterr().out

    with capsys.disabled():
        print(f"\nPrinted by save_week: {printed.strip()}")

    assert "Warning: saving 2027-W5, but later weeks are already in the history: 2027-W6" in printed
    assert path.read_text() == EXPECTED_TEXT
