"""Unit test 2 for library.graph.build_graph: a slot nobody can take is in the graph, with no edges.

Dummy data: L1 needs 1 qualified in the morning and 1 specialist at night.
  OP1 qualified on L1, available only in the morning.
The Night slot has no candidate, but it is still a node of the graph (with
0 edges), so the solver can report it as uncovered.
"""

from pathlib import Path

from library.graph import build_graph
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED_OPERATORS = {
    'OP1': {'shifts': ['Morning'], 'lines': {'L1': ['qualified', 'specialist', 'assistant']}, 'bipartite': 0},
}

EXPECTED_SLOTS = {
    'L1-Morning-qualified-1': {'line': 'L1', 'shift': 'Morning', 'role': 'qualified', 'bipartite': 1},
    'L1-Night-specialist-1': {'line': 'L1', 'shift': 'Night', 'role': 'specialist', 'bipartite': 1},
}

EXPECTED_EDGES = {
    ('OP1', 'L1-Morning-qualified-1'): 10,
}


def graph_contents(graph):
    """Operator nodes, slot nodes and edges of the graph, as plain dicts."""
    operators = {n: a for n, a in graph.nodes(data=True) if a["bipartite"] == 0}
    slots = {n: a for n, a in graph.nodes(data=True) if a["bipartite"] == 1}
    edges = {}
    for u, v, weight in graph.edges(data="weight"):
        operator, slot = (u, v) if u in operators else (v, u)
        edges[(operator, slot)] = weight
    return operators, slots, edges


def test_2_build_graph():
    data = load_planning_input("2027-W5", DATA_DIR)
    graph = build_graph(data)
    operators, slots, edges = graph_contents(graph)

    print(f"\nResult of build_graph for {data.period}: "
          f"{len(operators)} operators, {len(slots)} slots, {len(edges)} edges")
    print("  operators:")
    for node, attributes in operators.items():
        print(f"    {node}: {attributes}")
    print("  slots:")
    for node, attributes in slots.items():
        print(f"    {node}: {attributes} -> {graph.degree(node)} edge(s)")
    print("  edges:")
    for (operator, slot), weight in edges.items():
        print(f"    {operator} -- {slot}: {weight}")

    assert operators == EXPECTED_OPERATORS
    assert slots == EXPECTED_SLOTS
    assert edges == EXPECTED_EDGES
