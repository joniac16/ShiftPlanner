"""Unit test 1 for library.graph.build_edges: the 7 level -> slot role combinations, default weights.

    Dummy data: L1 Morning needs 1 specialist, 1 qualified and 1 assistant.
    All operators are available in the morning:
      OP1  specialist on L1 -> specialist 10 (exact), qualified 6, assistant 2
      OP2  qualified on L1  -> specialist 1 (last resort), qualified 10 (exact), assistant 3
      OP3  no training      -> assistant 10 (exact)
"""

from pathlib import Path

from library.graph import build_edges, build_operator_set, build_slot_set
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = [
    ('OP1', 'L1-Morning-specialist-1', 10),
    ('OP1', 'L1-Morning-qualified-1', 6),
    ('OP1', 'L1-Morning-assistant-1', 2),
    ('OP2', 'L1-Morning-specialist-1', 1),
    ('OP2', 'L1-Morning-qualified-1', 10),
    ('OP2', 'L1-Morning-assistant-1', 3),
    ('OP3', 'L1-Morning-assistant-1', 10),
]


def test_1_build_edges():
    data = load_planning_input("2027-W5", DATA_DIR)
    operator_set = build_operator_set(data)
    slot_set = build_slot_set(data)
    result = build_edges(data, operator_set, slot_set)

    print(f"\nResult of build_edges for {data.period}: {len(result)} edges")
    for edge in result:
        print(f"  {edge}")

    assert result == EXPECTED
