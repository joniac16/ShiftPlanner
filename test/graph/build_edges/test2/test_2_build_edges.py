"""Unit test 2 for library.graph.build_edges: no edge when the shift does not match.

    Dummy data: L1 needs 1 qualified in the morning and 1 at night.
      OP1  qualified on L1, available only at night -> only the Night slot
      OP2  qualified on L1, available morning and night -> both slots
"""

from pathlib import Path

from library.graph import build_edges, build_operator_set, build_slot_set
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = [
    ('OP1', 'L1-Night-qualified-1', 10),
    ('OP2', 'L1-Morning-qualified-1', 10),
    ('OP2', 'L1-Night-qualified-1', 10),
]


def test_2_build_edges():
    data = load_planning_input("2027-W5", DATA_DIR)
    operator_set = build_operator_set(data)
    slot_set = build_slot_set(data)
    result = build_edges(data, operator_set, slot_set)

    print(f"\nResult of build_edges for {data.period}: {len(result)} edges")
    for edge in result:
        print(f"  {edge}")

    assert result == EXPECTED
