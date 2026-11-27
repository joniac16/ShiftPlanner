"""Unit test 6 for library.solver.solve: maximize_matches=False takes the highest weight.

Dummy data: L1 needs 1 specialist in the morning and 1 assistant at night.
  OP1 specialist, morning and night -> Morning specialist (10) or Night assistant (2)
  OP2 qualified, morning only       -> Morning specialist as last resort (1)
With maximize_matches=True both slots would be covered (weight 3). With
False, OP1 as specialist (weight 10) wins: the Night assistant slot stays
uncovered (1 candidate, OP1) and OP2 is left unassigned.
"""

from pathlib import Path

from library.loader import load_planning_input
from library.models import Assignment, PlanningResult, WeekAllocation
from library.solver import solve

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = PlanningResult(
    allocation=WeekAllocation(period="2027-W5", assignments=[
        Assignment(operator="OP1", line="L1", shift="Morning", role="specialist"),
    ]),
    uncovered_slots={'L1-Night-assistant-1': 1},
    unassigned_operators=['OP2'],
    total_weight=10,
)


def test_6_solve():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = solve(data, maximize_matches=False)

    print(f"\nResult of solve for {result.allocation.period} (maximize_matches=False):")
    print("  assignments:")
    for assignment in result.allocation.assignments:
        print(f"    {assignment}")
    print(f"  uncovered slots (slot: candidates): {result.uncovered_slots}")
    print(f"  unassigned operators: {result.unassigned_operators}")
    print(f"  total weight: {result.total_weight}")

    assert result == EXPECTED
