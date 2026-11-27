"""Unit test 5 for library.solver.find_matching: nobody available: empty matching.

Dummy data: L1 Morning needs 1 qualified, but OP1 is not available that week.
"""

from pathlib import Path

from library.graph import build_graph
from library.loader import load_planning_input
from library.solver import find_matching

DATA_DIR = Path(__file__).parent / "data"

EXPECTED = {}


def test_5_find_matching():
    data = load_planning_input("2027-W5", DATA_DIR)
    graph = build_graph(data)
    result = find_matching(graph, maximize_matches=True)

    print(f"\nResult of find_matching for {data.period} (maximize_matches=True): "
          f"{len(result)} of {sum(1 for _, side in graph.nodes(data='bipartite') if side == 1)} slots covered")
    for slot, operator in result.items():
        print(f"  {slot} <- {operator} (weight {graph[slot][operator]['weight']})")

    assert result == EXPECTED
