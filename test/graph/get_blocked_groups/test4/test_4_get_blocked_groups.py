"""Unit test 4 for library.graph.get_blocked_groups: two restricted groups.

Dummy data: L1 is in RG1 (max 1, rest 1) and L2 in RG2 (max 2, rest 1).
Planning 2027-W5:
    W2 W3 W4
    L2 L2 L1   OP1 -> blocked from RG1 (1 week on L1 = max 1, no rest yet);
                      free in RG2 (run of 2 ended in W3, rested W4 = 1)
     .  L2 L2  OP2 -> blocked from RG2 (just worked 2 in a row)
"""

from pathlib import Path

from library.graph import get_blocked_groups
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {"OP1": {"RG1"}, "OP2": {"RG2"}}


def test_4_get_blocked_groups():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = get_blocked_groups(data)

    print(f"\nResult of get_blocked_groups for {data.period}: {result}")

    assert result == EXPECTED
