"""Unit test 2 for library.graph.build_operator_set: blocked operators.

Dummy data: L2 is in RG1 (max 2 consecutive weeks, min 1 rest week), L1 is
not restricted. Planning 2027-W5, after W3 and W4:
  OP1  specialist L2, worked L2 in W3 and W4 -> blocked: L2 removed, keeps L1
  OP2  no training, assistant on L2 in W3 and W4 -> blocked: L2 removed even
       as assistant, keeps L1 as assistant
  OP3  qualified L2, only W4 on L2 -> free: keeps L2
"""

from pathlib import Path

from library.graph import build_operator_set
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {
    "OP1": {"shifts": ["Morning"], "lines": {"L1": "qualified"}},
    "OP2": {"shifts": ["Morning"], "lines": {"L1": "assistant"}},
    "OP3": {"shifts": ["Morning"], "lines": {"L1": "assistant", "L2": "qualified"}},
}


def test_2_build_operator_set():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = build_operator_set(data)

    print(f"\nResult of build_operator_set for {data.period}:")
    for operator_id, options in result.items():
        print(f"  {operator_id}: {options}")

    assert result == EXPECTED
