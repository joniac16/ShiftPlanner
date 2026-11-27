"""Unit test 1 for library.solver.find_matching: every slot covered with the exact level.

Dummy data: L1 Morning needs 1 specialist, 1 qualified and 1 assistant.
  OP1 specialist, OP2 qualified, OP3 no training; all available in the morning.
The only best matching (total weight 30) puts everyone on their own level.
"""

from pathlib import Path

from library.graph import build_graph
from library.loader import load_planning_input
from library.solver import find_matching

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {
    'L1-Morning-specialist-1': 'OP1',
    'L1-Morning-qualified-1': 'OP2',
    'L1-Morning-assistant-1': 'OP3',
}


def test_1_find_matching():
    data = load_planning_input("2027-W5", DATA_DIR)
    graph = build_graph(data)
    result = find_matching(graph, maximize_matches=True)

    print(f"\nResult of find_matching for {data.period} (maximize_matches=True): "
          f"{len(result)} of {sum(1 for _, side in graph.nodes(data='bipartite') if side == 1)} slots covered")
    for slot, operator in result.items():
        print(f"  {slot} <- {operator} (weight {graph[slot][operator]['weight']})")

    assert result == EXPECTED
