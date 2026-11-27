"""Unit test 2 for library.solver.find_matching: maximize_matches=True covers as many slots as possible.

Dummy data: L1 needs 1 specialist in the morning and 1 assistant at night.
  OP1 specialist on L1, available morning and night
      -> Morning specialist (weight 10) or Night assistant (weight 3)
  OP2 qualified on L1, available only in the morning
      -> Morning specialist as last resort (weight 1)
Covering both slots (OP2 as specialist + OP1 as assistant, weight 4) beats
covering only one with more weight (OP1 as specialist, weight 10).
"""

from pathlib import Path

from library.graph import build_graph
from library.loader import load_planning_input
from library.solver import find_matching

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {
    'L1-Morning-specialist-1': 'OP2',
    'L1-Night-assistant-1': 'OP1',
}


def test_2_find_matching():
    data = load_planning_input("2027-W5", DATA_DIR)
    graph = build_graph(data)
    result = find_matching(graph, maximize_matches=True)

    print(f"\nResult of find_matching for {data.period} (maximize_matches=True): "
          f"{len(result)} of {sum(1 for _, side in graph.nodes(data='bipartite') if side == 1)} slots covered")
    for slot, operator in result.items():
        print(f"  {slot} <- {operator} (weight {graph[slot][operator]['weight']})")

    assert result == EXPECTED
