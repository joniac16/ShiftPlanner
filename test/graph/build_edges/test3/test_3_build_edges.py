"""Unit test 3 for library.graph.build_edges: no edge to a line the operator is blocked from.

    Dummy data: L1 is in RG1 (max 1 week, rest 1); L2 is not restricted.
    L1 Morning needs 1 qualified and 1 assistant; L2 Morning needs 1 assistant.
      OP1  qualified on L1, worked L1 in W4 -> blocked from RG1: no edge to any
           L1 slot (not even as assistant); only L2 as assistant
      OP2  qualified on L1, free -> L1 qualified, L1 assistant, L2 assistant
"""

from pathlib import Path

from library.graph import build_edges, build_operator_set, build_slot_set
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = [
    ('OP1', 'L2-Morning-assistant-1', 10),
    ('OP2', 'L1-Morning-qualified-1', 10),
    ('OP2', 'L1-Morning-assistant-1', 3),
    ('OP2', 'L2-Morning-assistant-1', 10),
]


def test_3_build_edges():
    data = load_planning_input("2027-W5", DATA_DIR)
    operator_set = build_operator_set(data)
    slot_set = build_slot_set(data)
    result = build_edges(data, operator_set, slot_set)

    print(f"\nResult of build_edges for {data.period}: {len(result)} edges")
    for edge in result:
        print(f"  {edge}")

    assert result == EXPECTED
