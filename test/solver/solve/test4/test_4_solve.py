"""Unit test 4 for library.solver.solve: an operator blocked by the history stays off the restricted line.

Dummy data: L1 is in RG1 (max 1 week, rest 1); L2 is not restricted. Both
need 1 qualified in the morning.
  OP1 qualified on L1 and L2, worked L1 in W4 -> blocked from RG1 this week.
  OP2 qualified on L1 only.
OP1 goes to L2 and OP2 to L1: total weight 20, nothing uncovered.
"""

from pathlib import Path

from library.loader import load_planning_input
from library.models import Assignment, PlanningResult, WeekAllocation
from library.solver import solve

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = PlanningResult(
    allocation=WeekAllocation(period="2027-W5", assignments=[
        Assignment(operator="OP2", line="L1", shift="Morning", role="qualified"),
        Assignment(operator="OP1", line="L2", shift="Morning", role="qualified"),
    ]),
    uncovered_slots={},
    unassigned_operators=[],
    total_weight=20,
)


def test_4_solve():
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
