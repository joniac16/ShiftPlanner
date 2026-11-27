"""Unit test 1 for library.graph.build_operator_set: levels and availability.

Dummy data: lines L1, L2, L3; only L1 and L2 run in 2027-W5. No history.
  OP1  specialist L1, qualified L2, specialist L3; available Morning + Night
       -> L1 specialist, L2 qualified (L3 left out: it does not run)
  OP2  no training; available Afternoon -> assistant on L1 and L2
  OP3  qualified L1; empty shift list  -> left out (not available)
  OP4  specialist L2; not in availabilities -> left out (not available)
"""

from pathlib import Path

from library.graph import build_operator_set
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {
    "OP1": {"shifts": ["Morning", "Night"], "lines": {"L1": "specialist", "L2": "qualified"}},
    "OP2": {"shifts": ["Afternoon"], "lines": {"L1": "assistant", "L2": "assistant"}},
}


def test_1_build_operator_set():
    data = load_planning_input("2027-W5", DATA_DIR)
    result = build_operator_set(data)

    print(f"\nResult of build_operator_set for {data.period}:")
    for operator_id, options in result.items():
        print(f"  {operator_id}: {options}")

    assert result == EXPECTED
