"""Unit test 2 for library.solver.solve: not enough operators: uncovered slots and their candidates.

Dummy data: L1 needs 1 specialist and 1 qualified in the morning, and 1
specialist at night. Only OP1 (qualified on L1, morning only) is available.
  - OP1 takes the Morning qualified slot (weight 10).
  - L1-Morning-specialist-1 stays uncovered with 1 candidate (OP1, who is
    needed elsewhere).
  - L1-Night-specialist-1 stays uncovered with 0 candidates (nobody can go).
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
    uncovered_slots={'L1-Morning-specialist-1': 1, 'L1-Night-specialist-1': 0},
    unassigned_operators=[],
    total_weight=10,
)


def test_2_solve():
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
