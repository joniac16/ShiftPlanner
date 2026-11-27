"""Unit test 1 for library.graph.build_graph: operator nodes, slot nodes and weighted edges.

Dummy data: L1 Morning needs 1 specialist, 1 qualified and 1 assistant.
  OP1 specialist on L1, OP2 qualified on L1, OP3 no training; all available
  in the morning. The graph has the 3 operators (bipartite=0) and the 3 slots
  (bipartite=1) with their attributes, and the 7 edges with default weights.
"""

from pathlib import Path

from library.graph import build_graph
from library.loader import load_planning_input

DATA_DIR = Path(__file__).parent / "data"

EXPECTED_OPERATORS = {
    'OP1': {'shifts': ['Morning'], 'lines': {'L1': ['specialist', 'qualified', 'assistant']}, 'bipartite': 0},
    'OP2': {'shifts': ['Morning'], 'lines': {'L1': ['qualified', 'specialist', 'assistant']}, 'bipartite': 0},
    'OP3': {'shifts': ['Morning'], 'lines': {'L1': ['assistant']}, 'bipartite': 0},
}

EXPECTED_SLOTS = {
    'L1-Morning-specialist-1': {'line': 'L1', 'shift': 'Morning', 'role': 'specialist', 'bipartite': 1},
    'L1-Morning-qualified-1': {'line': 'L1', 'shift': 'Morning', 'role': 'qualified', 'bipartite': 1},
    'L1-Morning-assistant-1': {'line': 'L1', 'shift': 'Morning', 'role': 'assistant', 'bipartite': 1},
}

EXPECTED_EDGES = {
    ('OP1', 'L1-Morning-specialist-1'): 10,
    ('OP1', 'L1-Morning-qualified-1'): 6,
    ('OP1', 'L1-Morning-assistant-1'): 3,
    ('OP2', 'L1-Morning-specialist-1'): 1,
    ('OP2', 'L1-Morning-qualified-1'): 10,
    ('OP2', 'L1-Morning-assistant-1'): 3,
    ('OP3', 'L1-Morning-assistant-1'): 10,
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


def test_1_build_graph():
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
