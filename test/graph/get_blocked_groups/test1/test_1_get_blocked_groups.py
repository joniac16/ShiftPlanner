"""Unit test 1 for library.graph.get_blocked_groups: the basic rule.

Dummy data: L2 is in RG1 (max 2 consecutive weeks, min 2 rest weeks), L1 is
not restricted. Planning 2027-W5. Weeks on L2 (X) per operator:
    W1 W2 W3 W4
     .  X  X  .   OP1 -> blocked (1 rest week out of 2; W4 on L1 does not count,
                           and W3 was as assistant, which also counts)
     .  .  X  X   OP2 -> blocked (just worked 2 in a row)
     X  X  .  .   OP3 -> free    (already rested 2 weeks)
     .  .  .  X   OP4 -> free    (only 1 week in a row)
"""

from pathlib import Path

from library.graph import get_blocked_groups
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {"OP1": {"RG1"}, "OP2": {"RG1"}}


def test_1_get_blocked_groups():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = get_blocked_groups(data)

    print(f"\nResult of get_blocked_groups for {data.period}: {result}")

    assert result == EXPECTED
