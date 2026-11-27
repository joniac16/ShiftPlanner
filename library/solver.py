"""Plan a week: find the best matching in the bipartite graph built by
`library.graph.build_graph` and turn it into a proposal.
"""

import networkx as nx

from library.graph import ALLOWED_ROLES, build_graph, get_blocked_groups
from library.loader import DataError
from library.models import Assignment, MatchWeights, PlanningInput, PlanningResult, WeekAllocation


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


def build_allocation(period: str, matching: dict[str, str], graph: nx.Graph) -> WeekAllocation:
    """Turn a matching (slot id -> operator id) into the week's allocation.

    Each pair becomes an Assignment with the slot's line, shift and role (taken
    from the slot node's attributes in the graph). The role is the role of the
    slot, not the operator's level: a specialist in a qualified slot is stored
    as "qualified". Assignments follow the order of `matching`.
    """
    assignments = []
    for slot_id, operator_id in matching.items():
        slot = graph.nodes[slot_id]
        assignments.append(Assignment(operator=operator_id, line=slot["line"], shift=slot["shift"], role=slot["role"]))
    return WeekAllocation(period=period, assignments=assignments)


def solve(
    data: PlanningInput,
    weights: MatchWeights | None = None,
    maximize_matches: bool = True,
) -> PlanningResult:
    """Plan `data.period`: build the graph, find the best matching and report.

    - weights: edge weights (`MatchWeights`); defaults if None.
    - maximize_matches: True -> cover as many slots as possible, then highest
      weight; False -> highest weight only (see `find_matching`).

    Always returns a plan, even if some slots cannot be covered. The report:
      - uncovered_slots: slot id -> number of candidate operators it had
        (0: nobody could take it; more: its candidates were needed elsewhere),
      - unassigned_operators: operators in the graph (available that week and
        not blocked everywhere) who got no slot,
      - total_weight: sum of the weights of the chosen edges.
    Nothing is written to disk.
    """
    graph = build_graph(data, weights)
    matching = find_matching(graph, maximize_matches)
    allocation = build_allocation(data.period, matching, graph)

    slots = [node for node, side in graph.nodes(data="bipartite") if side == 1]
    operators = [node for node, side in graph.nodes(data="bipartite") if side == 0]
    assigned = set(matching.values())

    return PlanningResult(
        allocation=allocation,
        uncovered_slots={slot: graph.degree(slot) for slot in slots if slot not in matching},
        unassigned_operators=[operator for operator in operators if operator not in assigned],
        total_weight=sum(graph[slot][operator]["weight"] for slot, operator in matching.items()),
    )


def validate_week(allocation: WeekAllocation, data: PlanningInput) -> None:
    """Check that a week's allocation follows the rules. Raises DataError if not.

    Used before saving a week to the history, so a plan edited by hand cannot
    bring errors in. For every assignment:
      - the operator exists and appears only once in the week,
      - the operator is available that week, on that shift,
      - the line runs that week, and runs that shift,
      - the operator is not blocked from the line's restricted group,
      - the role is allowed for the operator's level on the line (ALLOWED_ROLES).
    And no (line, shift, role) has more operators than the demand asks for.
    Fewer is fine: the solver may leave slots uncovered.
    """
    if allocation.period != data.period:
        raise DataError(f"Allocation is for {allocation.period}, but the planning data is for {data.period}")

    demand = {(d.line, s.name): s.staff for d in data.demands for s in d.shifts}
    running_lines = {d.line for d in data.demands}
    blocked = get_blocked_groups(data)

    seen: set[str] = set()
    count: dict[tuple[str, str, str], int] = {}

    for a in allocation.assignments:
        if a.operator not in data.operators:
            raise DataError(f"Unknown operator {a.operator}")
        if a.operator in seen:
            raise DataError(f"Operator {a.operator} is assigned more than once in {data.period}")
        seen.add(a.operator)

        availability = data.availabilities.get(a.operator)
        if availability is None or not availability.shifts:
            raise DataError(f"Operator {a.operator} is not available in {data.period}")
        if a.shift not in availability.shifts:
            raise DataError(f"Operator {a.operator} is not available on shift {a.shift} in {data.period}")

        if a.line not in running_lines:
            raise DataError(f"Line {a.line} does not run in {data.period}")
        if (a.line, a.shift) not in demand:
            raise DataError(f"Line {a.line} does not run shift {a.shift} in {data.period}")

        group = data.lines[a.line].restricted_group
        if group is not None and group.id in blocked.get(a.operator, set()):
            raise DataError(f"Operator {a.operator} is blocked from restricted group {group.id} (line {a.line}) in {data.period}")

        level = data.operators[a.operator].lines.get(a.line)
        if a.role not in ALLOWED_ROLES[level]:
            raise DataError(f"Operator {a.operator} ({level or 'no training'} on {a.line}) cannot take a {a.role} slot")

        key = (a.line, a.shift, a.role)
        count[key] = count.get(key, 0) + 1

    for (line, shift, role), n in count.items():
        needed = getattr(demand[(line, shift)], role)
        if n > needed:
            raise DataError(f"Line {line}, shift {shift} needs {needed} {role}(s), got {n}")
