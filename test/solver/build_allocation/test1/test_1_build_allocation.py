"""Unit test 1 for library.solver.build_allocation: every pair of the matching becomes an Assignment.

Dummy data: L1 Morning needs 1 specialist and 1 qualified; L2 Night needs 1
assistant. OP1 and OP2 are specialists on L1, OP3 has no training.
The matching is written by hand (not computed), so only build_allocation is
tested:
  L1-Morning-specialist-1 <- OP1   -> role "specialist"
  L1-Morning-qualified-1  <- OP2   -> role "qualified" (the slot's role, even
                                      though OP2 is a specialist)
  L2-Night-assistant-1    <- OP3   -> role "assistant"
"""

from pathlib import Path

from library.graph import build_graph
from library.loader import load_planning_input
from library.models import Assignment, WeekAllocation
from library.solver import build_allocation

DATA_DIR = Path(__file__).parent / "data"

MATCHING = {
    "L1-Morning-specialist-1": "OP1",
    "L1-Morning-qualified-1": "OP2",
    "L2-Night-assistant-1": "OP3",
}

EXPECTED = WeekAllocation(period="2027-W5", assignments=[
    Assignment(operator="OP1", line="L1", shift="Morning", role="specialist"),
    Assignment(operator="OP2", line="L1", shift="Morning", role="qualified"),
    Assignment(operator="OP3", line="L2", shift="Night", role="assistant"),
])


def test_1_build_allocation():
    data = load_planning_input("2027-W5", DATA_DIR)
    graph = build_graph(data)
    result = build_allocation(data.period, MATCHING, graph)

    print(f"\nResult of build_allocation for {result.period}: {len(result.assignments)} assignments")
    for assignment in result.assignments:
        print(f"  {assignment}")

    assert result == EXPECTED
