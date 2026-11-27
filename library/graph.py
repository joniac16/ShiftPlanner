"""Build the bipartite graph that the solver uses to plan a week.

The planning problem is modelled as a bipartite graph:
  - left side: the operators available that week (`build_operator_set`),
  - right side: the individual positions to cover (slots),
  - edges: an operator can take a slot; each edge has a weight.
The solver looks for a maximum-cardinality matching (as many slots covered as
possible) and, among those, the one with maximum total weight.

Assignment rules
----------------
An operator's level on a line decides which slots of that line they can take:

    Operator level on the line   Can take a slot of
    --------------------------   ------------------------------------------------
    specialist                   specialist, qualified, assistant
    qualified                    qualified, specialist (last resort), assistant
    no training on that line     assistant only

- Any operator can be an assistant on any line running that week, even with no
  training on it (it is a waste of training, so it should only happen when
  operators are left over; the weights take care of that).
- Each operator covers at most one slot per week.
- Restricted groups block every role: an operator who must rest from a group
  cannot go to any of its lines, not even as an assistant.
- Preferences between the allowed options are given by edge weights, which are
  parameters that can be changed to experiment with the result.
- The history stores the role of the slot taken, not the operator's level.

Restricted groups and history
-----------------------------
After working `max_consecutive_weeks` weeks in a row on lines of a restricted
group (any shift, any role), an operator must stay off all the group's lines for
at least `min_rest_weeks` weeks. A week with no history counts as not worked in
the group.
"""

from datetime import date, timedelta

import networkx as nx

from library.models import MatchWeights, PlanningInput
from library.utils import iso_week_to_date

ONE_WEEK = timedelta(weeks=1)

# Slot roles an operator can take on a line, by their level on it (see the
# assignment rules above). Order: from the most to the least natural option.
ALLOWED_ROLES = {
    "specialist": ["specialist", "qualified", "assistant"],
    "qualified": ["qualified", "specialist", "assistant"],
    None: ["assistant"],  # no training on the line
}


def get_blocked_groups(data: PlanningInput) -> dict[str, set[str]]:
    """Return the restricted groups each operator is blocked from in `data.period`.

    Result: operator id -> set of restricted group ids. Operators with no
    blocked group are not included.

    An operator is blocked from a group if, looking back from the planned week,
    their last run of consecutive weeks in the group lasted at least
    `max_consecutive_weeks`, and fewer than `min_rest_weeks` weeks have passed
    since that run ended.

    Example (max 2 consecutive weeks, min 2 rest weeks), planning W5:
        W1 W2 W3 W4 | W5
         .  X  X  . | blocked (1 rest week out of 2)
         .  .  X  X | blocked (just worked 2 in a row)
         X  X  .  . | free    (already rested 2 weeks)
         .  .  .  X | free    (only 1 week in a row)
    """
    # Lines of each restricted group, and the group itself.
    groups: dict[str, tuple] = {}
    for line in data.lines.values():
        if line.restricted_group is not None:
            group = line.restricted_group
            groups.setdefault(group.id, (group, set()))[1].add(line.id)

    planned_week = iso_week_to_date(data.period)
    blocked: dict[str, set[str]] = {}

    for group_id, (group, group_lines) in groups.items():
        # Weeks (as Monday dates) each operator worked on a line of the group.
        weeks_worked: dict[str, set[date]] = {}
        for week in data.history:
            monday = iso_week_to_date(week.period)
            for assignment in week.assignments:
                if assignment.line in group_lines:
                    weeks_worked.setdefault(assignment.operator, set()).add(monday)

        for operator_id, weeks in weeks_worked.items():
            past_weeks = {w for w in weeks if w < planned_week}
            if not past_weeks:
                continue

            # Length of the last run of consecutive weeks in the group.
            last_week = max(past_weeks)
            run_length = 0
            week = last_week
            while week in past_weeks:
                run_length += 1
                week -= ONE_WEEK

            # Weeks rested since the run ended (weeks between it and the planned week).
            rest_weeks = (planned_week - last_week).days // 7 - 1

            if run_length >= group.max_consecutive_weeks and rest_weeks < group.min_rest_weeks:
                blocked.setdefault(operator_id, set()).add(group_id)

    return blocked


def build_operator_set(data: PlanningInput) -> dict[str, dict]:
    """Build the operator side of the bipartite graph for `data.period`.

    Result: operator id -> {"shifts": [...], "lines": {line id: [roles]}}, where
      - "shifts" are the shifts the operator can cover that week,
      - "lines" are all the lines running that week (in demands) the operator
        can go to, with every slot role they can take on each one, following
        the assignment rules (`ALLOWED_ROLES`):
            specialist on the line -> ["specialist", "qualified", "assistant"]
            qualified on the line  -> ["qualified", "specialist", "assistant"]
            no training on it      -> ["assistant"]
        Lines of restricted groups the operator is blocked from (see
        `get_blocked_groups`) are left out.

    Operators who are not available that week (no shifts) or who cannot go to
    any running line are left out.
    """
    running_lines = [demand.line for demand in data.demands]
    blocked = get_blocked_groups(data)

    operator_set: dict[str, dict] = {}

    for operator_id, operator in data.operators.items():
        availability = data.availabilities.get(operator_id)
        if availability is None or not availability.shifts:
            continue

        blocked_groups = blocked.get(operator_id, set())
        lines: dict[str, list[str]] = {}
        for line_id in running_lines:
            group = data.lines[line_id].restricted_group
            if group is not None and group.id in blocked_groups:
                continue
            level = operator.lines.get(line_id)
            lines[line_id] = list(ALLOWED_ROLES[level])

        if not lines:
            continue

        operator_set[operator_id] = {"shifts": list(availability.shifts), "lines": lines}

    return operator_set


SLOT_ROLES = ("specialist", "qualified", "assistant")


def build_slot_set(data: PlanningInput) -> dict[str, dict]:
    """Build the slot side of the bipartite graph for `data.period`.

    Each position needed in `data.demands` becomes one slot (one graph node), so
    a shift that needs 2 qualified operators gives 2 qualified slots.

    Result: slot id -> {"line": ..., "shift": ..., "role": ...}, with ids like
    "L1-Morning-qualified-2" (numbered from 1, no leading zeros). Roles with 0
    positions give no slot. Order: lines and shifts as in the demands, and
    within a shift specialist, qualified, assistant.
    """
    slot_set: dict[str, dict] = {}

    for demand in data.demands:
        for shift in demand.shifts:
            for role in SLOT_ROLES:
                for number in range(1, getattr(shift.staff, role) + 1):
                    slot_id = f"{demand.line}-{shift.name}-{role}-{number}"
                    slot_set[slot_id] = {"line": demand.line, "shift": shift.name, "role": role}

    return slot_set


def build_edges(
    data: PlanningInput,
    operator_set: dict[str, dict],
    slot_set: dict[str, dict],
    weights: MatchWeights | None = None,
) -> list[tuple[str, str, float]]:
    """Build the weighted edges of the bipartite graph.

    There is an edge between an operator and a slot when the slot's shift is in
    the operator's shifts, the slot's line is in the operator's lines (so it is
    running and not blocked) and the slot's role is one of the roles the
    operator can take on that line. Its weight depends on the slot's role and
    on who fills it (the operator's level on the line, from `data.operators`):

        slot role    filled by                    weight field
        specialist   specialist                   specialist_slot_specialist
        specialist   qualified (last resort)      specialist_slot_qualified
        qualified    qualified                    qualified_slot_qualified
        qualified    specialist                   qualified_slot_specialist
        assistant    no training on the line      assistant_slot_untrained
        assistant    specialist or qualified      assistant_slot_trained

    Result: list of (operator id, slot id, weight), ready for
    `G.add_weighted_edges_from`. Order: operators as in `operator_set`, slots as
    in `slot_set`. `weights` defaults to `MatchWeights()`.
    """
    if weights is None:
        weights = MatchWeights()

    # (operator level on the line, slot role) -> weight
    weight_by_level_and_role = {
        ("specialist", "specialist"): weights.specialist_slot_specialist,
        ("qualified", "specialist"): weights.specialist_slot_qualified,
        ("qualified", "qualified"): weights.qualified_slot_qualified,
        ("specialist", "qualified"): weights.qualified_slot_specialist,
        (None, "assistant"): weights.assistant_slot_untrained,
        ("specialist", "assistant"): weights.assistant_slot_trained,
        ("qualified", "assistant"): weights.assistant_slot_trained,
    }

    edges: list[tuple[str, str, float]] = []

    for operator_id, options in operator_set.items():
        for slot_id, slot in slot_set.items():
            if slot["shift"] not in options["shifts"]:
                continue
            roles = options["lines"].get(slot["line"])
            if roles is None or slot["role"] not in roles:
                continue
            level = data.operators[operator_id].lines.get(slot["line"])
            edges.append((operator_id, slot_id, weight_by_level_and_role[(level, slot["role"])]))

    return edges


def build_graph(data: PlanningInput, weights: MatchWeights | None = None) -> nx.Graph:
    """Build the weighted bipartite graph of `data.period`.

    Nodes:
      - operators (`build_operator_set`), with attribute bipartite=0 and their
        options ("shifts", "lines") as attributes,
      - slots (`build_slot_set`), with attribute bipartite=1 and "line",
        "shift", "role" as attributes. Slots no operator can take are included
        too (with no edges), so they show up as uncovered.
    Edges: `build_edges`, with their weight in the "weight" attribute.
    `weights` defaults to `MatchWeights()`.
    """
    operator_set = build_operator_set(data)
    slot_set = build_slot_set(data)
    edges = build_edges(data, operator_set, slot_set, weights)

    graph = nx.Graph()
    graph.add_nodes_from(operator_set.items(), bipartite=0)
    graph.add_nodes_from(slot_set.items(), bipartite=1)
    graph.add_weighted_edges_from(edges)
    return graph
