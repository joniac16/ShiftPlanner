"""Unit test for library.loader.load_history.

Dummy data: data/history/ with three weeks: 2026-W53, 2027-W2 and 2027-W10.
As text they would sort as 2026-W53, 2027-W10, 2027-W2, so the test checks
that the result is in chronological order: 2026-W53, 2027-W2, 2027-W10.
"""

from pathlib import Path

from library.loader import load_history
from library.models import Assignment, WeekAllocation

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = [
    WeekAllocation(period="2026-W53", assignments=[
        Assignment(operator="OP1", line="L1", shift="Morning", role="specialist"),
    ]),
    WeekAllocation(period="2027-W2", assignments=[
        Assignment(operator="OP1", line="L1", shift="Night", role="specialist"),
        Assignment(operator="OP3", line="L1", shift="Night", role="assistant"),
    ]),
    WeekAllocation(period="2027-W10", assignments=[
        Assignment(operator="OP2", line="L2", shift="Afternoon", role="qualified"),
    ]),
]


def test_load_history():
    result = load_history(DATA_DIR)

    print("\nResult of load_history:")
    for week in result:
        print(f"  {week.period}:")
        for assignment in week.assignments:
            print(f"    {assignment}")

    assert result == EXPECTED
