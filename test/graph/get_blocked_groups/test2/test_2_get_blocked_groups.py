"""Unit test 2 for library.graph.get_blocked_groups: no restricted groups.

Dummy data: L1 and L2 have no restricted group. OP1 and OP2 have worked on
the same line for four weeks in a row, but nobody can be blocked.
"""

from pathlib import Path

from library.graph import get_blocked_groups
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"


def test_2_get_blocked_groups():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = get_blocked_groups(data)

    print(f"\nResult of get_blocked_groups for {data.period}: {result}")

    assert result == {}
