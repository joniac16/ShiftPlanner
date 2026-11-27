"""Unit test 3 for library.graph.get_blocked_groups: a week missing from the history.

Dummy data: L1 is in RG1 (max 2 consecutive weeks, min 3 rest weeks).
History has W1, W2 and W4; W3 is missing, so it counts as not worked.
Planning 2027-W5:
    W1 W2 W3 W4
     X  X  -  .   OP1 -> blocked (run of 2 ended in W2; rested W3 and W4 = 2 < 3)
     .  X  -  X   OP2 -> free    (the missing W3 breaks the run: only 1 in a row)
"""

from pathlib import Path

from library.graph import get_blocked_groups
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {"OP1": {"RG1"}}


def test_3_get_blocked_groups():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = get_blocked_groups(data)

    print(f"\nResult of get_blocked_groups for {data.period}: {result}")

    assert result == EXPECTED
