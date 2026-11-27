"""Unit test 1 for library.solver.solve: every slot covered with the exact level.

Dummy data: L1 Morning needs 1 specialist, 1 qualified and 1 assistant.
  OP1 specialist, OP2 qualified, OP3 no training; all available in the morning.
Everybody goes to their own level: no uncovered slots, nobody left over,
total weight 10 + 10 + 10 = 30.
"""

from pathlib import Path

from library.loader import load_planning_input
from library.models import Assignment, PlanningResult, WeekAllocation
from library.solver import solve

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = PlanningResult(
    allocation=WeekAllocation(period="2027-W5", assignments=[
        Assignment(operator="OP1", line="L1", shift="Morning", role="specialist"),
        Assignment(operator="OP2", line="L1", shift="Morning", role="qualified"),
        Assignment(operator="OP3", line="L1", shift="Morning", role="assistant"),
    ]),
    uncovered_slots={},
    unassigned_operators=[],
    total_weight=30,
)


def test_1_solve():
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
