"""Unit test 3 for library.solver.find_matching: maximize_matches=False takes the highest weight.

Same dummy data as test2:
  OP1 -> Morning specialist (10) or Night assistant (3)
  OP2 -> Morning specialist (1)
Without maximizing the number of matches, OP1 as specialist (weight 10) beats
covering both slots (weight 4), so the Night assistant slot stays uncovered.
"""

from pathlib import Path

from library.graph import build_graph
from library.loader import load_planning_input
from library.solver import find_matching

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {
    'L1-Morning-specialist-1': 'OP1',
}


def test_3_find_matching():
    data = load_planning_input("2027-W5", DATA_DIR)
    graph = build_graph(data)
    result = find_matching(graph, maximize_matches=False)

    print(f"\nResult of find_matching for {data.period} (maximize_matches=False): "
          f"{len(result)} of {sum(1 for _, side in graph.nodes(data='bipartite') if side == 1)} slots covered")
    for slot, operator in result.items():
        print(f"  {slot} <- {operator} (weight {graph[slot][operator]['weight']})")

    assert result == EXPECTED
