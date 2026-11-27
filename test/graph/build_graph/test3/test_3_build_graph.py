"""Unit test 3 for library.graph.build_graph: custom weights reach the edges.

Same dummy data as test1, built with MatchWeights(specialist_as_qualified=7,
qualified_as_specialist=0.5): only those two edges change.
"""

from pathlib import Path

from library.graph import build_graph
from library.loader import load_planning_input
from library.models import MatchWeights

DATA_DIR = Path(__file__).parent / "data"

WEIGHTS = MatchWeights(specialist_as_qualified=7, qualified_as_specialist=0.5)

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
    ('OP1', 'L1-Morning-qualified-1'): 7,
    ('OP1', 'L1-Morning-assistant-1'): 2,
    ('OP2', 'L1-Morning-specialist-1'): 0.5,
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


def test_3_build_graph():
    data = load_planning_input("2027-W5", DATA_DIR)
    graph = build_graph(data, WEIGHTS)
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
