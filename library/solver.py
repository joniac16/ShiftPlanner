"""Plan a week: find the best matching in the bipartite graph built by
`library.graph.build_graph` and turn it into a proposal.
"""

import networkx as nx


def find_matching(graph: nx.Graph, maximize_matches: bool = True) -> dict[str, str]:
    """Find the best matching of the graph. Returns a dict: slot id -> operator id.

    - maximize_matches=True: cover as many slots as possible and, among the
      matchings that do, take the one with the highest total weight.
    - maximize_matches=False: take the highest total weight, even if fewer
      slots are covered.

    Uses `networkx.max_weight_matching` (Edmonds' blossom algorithm). Slots
    are the nodes with bipartite=1; the result follows their order in the graph.
    """
    pairs = nx.max_weight_matching(graph, maxcardinality=maximize_matches, weight="weight")

    operator_of_slot: dict[str, str] = {}
    for u, v in pairs:
        slot, operator = (u, v) if graph.nodes[u]["bipartite"] == 1 else (v, u)
        operator_of_slot[slot] = operator

    slot_order = [node for node, side in graph.nodes(data="bipartite") if side == 1]
    return {slot: operator_of_slot[slot] for slot in slot_order if slot in operator_of_slot}
