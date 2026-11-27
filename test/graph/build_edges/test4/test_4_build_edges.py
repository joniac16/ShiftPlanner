"""Unit test 4 for library.graph.build_edges: custom weights.

    Same dummy data as test1, but with custom weights: every edge takes the
    value of its weight field instead of the default one.
"""

from pathlib import Path

from library.graph import build_edges, build_operator_set, build_slot_set
from library.loader import load_planning_input
from library.models import MatchWeights

DATA_DIR = Path(__file__).parent / "data"

WEIGHTS = MatchWeights(
    exact=5,
    specialist_as_qualified=4,
    qualified_as_assistant=0.5,
    specialist_as_assistant=0.25,
    qualified_as_specialist=0.1,
)

EXPECTED = [
    ('OP1', 'L1-Morning-specialist-1', 5),
    ('OP1', 'L1-Morning-qualified-1', 4),
    ('OP1', 'L1-Morning-assistant-1', 0.25),
    ('OP2', 'L1-Morning-specialist-1', 0.1),
    ('OP2', 'L1-Morning-qualified-1', 5),
    ('OP2', 'L1-Morning-assistant-1', 0.5),
    ('OP3', 'L1-Morning-assistant-1', 5),
]


def test_4_build_edges():
    data = load_planning_input("2027-W5", DATA_DIR)
    operator_set = build_operator_set(data)
    slot_set = build_slot_set(data)
    result = build_edges(data, operator_set, slot_set, WEIGHTS)

    print(f"\nResult of build_edges for {data.period}: {len(result)} edges")
    for edge in result:
        print(f"  {edge}")

    assert result == EXPECTED
