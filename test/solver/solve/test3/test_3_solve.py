"""Unit test 3 for library.solver.solve: operators left over.

Dummy data: L1 Morning needs only 1 qualified.
  OP1 qualified (weight 10), OP3 specialist (specialist as qualified, weight 6),
  OP2 no training (cannot take a qualified slot).
OP1 takes the slot; OP2 and OP3 are reported as unassigned.
"""

from pathlib import Path

from library.loader import load_planning_input
from library.models import Assignment, PlanningResult, WeekAllocation
from library.solver import solve

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = PlanningResult(
    allocation=WeekAllocation(period="2027-W5", assignments=[
        Assignment(operator="OP1", line="L1", shift="Morning", role="qualified"),
    ]),
    uncovered_slots={},
    unassigned_operators=['OP2', 'OP3'],
    total_weight=10,
)


def test_3_solve():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = solve(data)

    print(f"\nResult of solve for {result.allocation.period}:")
    print("  assignments:")
    for assignment in result.allocation.assignments:
        print(f"    {assignment}")
    print(f"  uncovered slots (slot: candidates): {result.uncovered_slots}")
    print(f"  unassigned operators: {result.unassigned_operators}")
    print(f"  total weight: {result.total_weight}")

    assert result == EXPECTED
