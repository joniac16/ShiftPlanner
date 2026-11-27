"""Unit test 5 for library.solver.solve: custom weights change the choice.

Dummy data: L1 Morning needs 1 qualified and 1 assistant; OP1 is a specialist
and OP2 qualified. Both slots are always covered; the weights decide who
goes where:
  - default weights: OP2 qualified (10) + OP1 assistant (2) = 12
                     beats OP1 qualified (6) + OP2 assistant (3) = 9
  - custom weights (specialist_as_qualified=9, specialist_as_assistant=0.5):
                     OP1 qualified (9) + OP2 assistant (3) = 12
                     beats OP2 qualified (10) + OP1 assistant (0.5) = 10.5
This test uses the custom weights.
"""

from pathlib import Path

from library.loader import load_planning_input
from library.models import Assignment, MatchWeights, PlanningResult, WeekAllocation
from library.solver import solve

DATA_DIR = Path(__file__).parent / "data"

WEIGHTS = MatchWeights(specialist_as_qualified=9, specialist_as_assistant=0.5)

EXPECTED = PlanningResult(
    allocation=WeekAllocation(period="2027-W5", assignments=[
        Assignment(operator="OP1", line="L1", shift="Morning", role="qualified"),
        Assignment(operator="OP2", line="L1", shift="Morning", role="assistant"),
    ]),
    uncovered_slots={},
    unassigned_operators=[],
    total_weight=12,
)


def test_5_solve():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = solve(data, WEIGHTS)

    print(f"\nResult of solve for {result.allocation.period} (custom weights):")
    print("  assignments:")
    for assignment in result.allocation.assignments:
        print(f"    {assignment}")
    print(f"  uncovered slots (slot: candidates): {result.uncovered_slots}")
    print(f"  unassigned operators: {result.unassigned_operators}")
    print(f"  total weight: {result.total_weight}")

    assert result == EXPECTED
