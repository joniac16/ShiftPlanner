"""Unit test 3 for library.graph.build_operator_set: no possible line.

Dummy data: L2 is in RG1 (max 1, rest 1); only L2 runs in 2027-W5.
  OP1  worked L2 in W4 -> blocked from RG1; L2 is the only running line, so
       OP1 has nowhere to go and is left out (even though trained on L1)
  OP2  no training, free -> assistant on L2
"""

from pathlib import Path

from library.graph import build_operator_set
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {
    "OP2": {"shifts": ["Morning"], "lines": {"L2": ["assistant"]}},
}


def test_3_build_operator_set():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = build_operator_set(data)

    print(f"\nResult of build_operator_set for {data.period}:")
    for operator_id, options in result.items():
        print(f"  {operator_id}: {options}")

    assert result == EXPECTED
