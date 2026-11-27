"""Unit test 2 for library.solver.build_allocation: an empty matching gives an allocation with no assignments.

Same dummy data as test1, with an empty matching: the allocation keeps the
period and has an empty list of assignments.
"""

from pathlib import Path

from library.graph import build_graph
from library.loader import load_planning_input
from library.models import Assignment, WeekAllocation
from library.solver import build_allocation

DATA_DIR = Path(__file__).parent / "data"

MATCHING = {}

EXPECTED = WeekAllocation(period="2027-W5", assignments=[])


def test_2_build_allocation():
    data = load_planning_input("2027-W5", DATA_DIR)
    graph = build_graph(data)
    result = build_allocation(data.period, MATCHING, graph)

    print(f"\nResult of build_allocation for {result.period}: {len(result.assignments)} assignments")
    for assignment in result.assignments:
        print(f"  {assignment}")

    assert result == EXPECTED
