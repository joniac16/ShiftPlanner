"""ShiftPlanner front end (Streamlit).

Run it with:
    streamlit run app.py

Four screens, chosen in the sidebar:
  - Plan:     choose the range of weeks, the objective, overwrite and weights,
              run `plan_weeks` and see the report of every week.
  - Schedule: one week of the history as a table of lines x shifts.
  - Data:     operators and their training, lines, and each week's demand
              and availability.
  - Graph:    the bipartite graph of a week (a few lines and shifts), with
              the edges of the matching highlighted. For the thesis.

The app only displays data and calls functions of `library/`; all the logic
(and its tests) lives there.
"""

import contextlib
import io
import json
from dataclasses import fields, replace
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from library.graph import build_graph
from library.loader import DataError, load_demands, load_history, load_lines, load_operators, load_planning_input
from library.models import MatchWeights
from library.planner import plan_weeks
from library.solver import find_matching
from library.utils import iso_week_to_date, sort_iso_weeks

SHIFT_ORDER = ["Morning", "Afternoon", "Night"]
ROLE_ORDER = ["specialist", "qualified", "assistant"]
WEIGHT_LABELS = {
    "exact": "Exact level (incl. untrained as assistant)",
    "specialist_as_qualified": "Specialist as qualified",
    "qualified_as_assistant": "Qualified as assistant",
    "specialist_as_assistant": "Specialist as assistant",
    "qualified_as_specialist": "Qualified as specialist (last resort)",
}


# --- Helpers -------------------------------------------------------------------


def source_weeks(data_dir: Path) -> list[str]:
    """Weeks that have a demand in source/demands.json, chronologically."""
    path = data_dir / "source" / "demands.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return sort_iso_weeks(list(json.load(f)))


def shift_sort_key(shift: str):
    return (SHIFT_ORDER.index(shift) if shift in SHIFT_ORDER else len(SHIFT_ORDER), shift)


def weights_form(key: str) -> MatchWeights:
    """One number input per edge weight, with the defaults of MatchWeights."""
    defaults = MatchWeights()
    values = {}
    for field in fields(MatchWeights):
        values[field.name] = st.number_input(
            WEIGHT_LABELS[field.name], min_value=0.0, value=float(getattr(defaults, field.name)),
            step=0.5, key=f"{key}-{field.name}",
        )
    return MatchWeights(**values)


# --- Screens -------------------------------------------------------------------


def plan_screen(data_dir: Path) -> None:
    st.header("Plan weeks")
    st.write("Plans every week of the range in order and saves them to the history, "
             "only if all of them can be planned.")

    weeks = source_weeks(data_dir)
    planned = {w.period for w in load_history(data_dir)}
    pending = [w for w in weeks if w not in planned] or weeks
    # Default range: the weeks with data that are not in the history yet.
    first = iso_week_to_date(pending[0]).isocalendar() if pending else (2027, 1, 1)
    last = iso_week_to_date(pending[-1]).isocalendar() if pending else first

    with st.form("plan"):
        c1, c2, c3, c4 = st.columns(4)
        start_year = c1.number_input("Start year", value=int(first[0]), step=1)
        start_week = c2.number_input("Start week", min_value=1, max_value=53, value=int(first[1]))
        end_year = c3.number_input("End year", value=int(last[0]), step=1)
        end_week = c4.number_input("End week", min_value=1, max_value=53, value=int(last[1]))

        objective = st.radio("Objective", ["Maximum number of covered slots, then highest weight",
                                           "Highest weight only"])
        overwrite = st.checkbox("Overwrite weeks already in the history")
        with st.expander("Edge weights"):
            weights = weights_form("plan")
        submitted = st.form_submit_button("Plan", type="primary")

    if weeks:
        st.caption(f"Weeks with data in source: {', '.join(weeks)}")
    if not submitted:
        return

    printed = io.StringIO()
    try:
        with contextlib.redirect_stdout(printed):
            results = plan_weeks(
                int(start_year), int(start_week), int(end_year), int(end_week),
                data_dir=data_dir, weights=weights,
                maximize_matches=objective.startswith("Maximum number"), overwrite=overwrite,
            )
    except DataError as error:
        st.error(str(error))
        return

    for line in printed.getvalue().splitlines():
        st.warning(line)
    st.success(f"Planned and saved {len(results)} week(s) to {data_dir / 'history'}.")

    names = {o.id: o.name for o in load_operators(data_dir).values()}
    for result in results:
        allocation = result.allocation
        st.subheader(allocation.period)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Assignments", len(allocation.assignments))
        c2.metric("Uncovered slots", len(result.uncovered_slots))
        c3.metric("Unassigned operators", len(result.unassigned_operators))
        c4.metric("Total weight", f"{result.total_weight:g}")
        if result.uncovered_slots:
            st.write("Uncovered slots (0 candidates: nobody could take it; more: its candidates were needed elsewhere):")
            st.dataframe(pd.DataFrame(
                [{"slot": slot, "candidates": n} for slot, n in result.uncovered_slots.items()]),
                hide_index=True)
        if result.unassigned_operators:
            with st.expander("Unassigned operators"):
                st.write(", ".join(f"{o} ({names.get(o, '?')})" for o in result.unassigned_operators))


def schedule_screen(data_dir: Path) -> None:
    st.header("Schedule")
    history = load_history(data_dir)
    if not history:
        st.info("The history is empty.")
        return

    period = st.selectbox("Week", [w.period for w in history], index=len(history) - 1)
    week = next(w for w in history if w.period == period)
    operators = load_operators(data_dir)
    lines = load_lines(data_dir)

    # Lines x shifts table, with names and roles.
    cells: dict[tuple[str, str], list[str]] = {}
    for a in week.assignments:
        name = operators[a.operator].name if a.operator in operators else a.operator
        cells.setdefault((a.line, a.shift), []).append((ROLE_ORDER.index(a.role), f"{name} ({a.role})"))
    shifts = sorted({shift for _, shift in cells}, key=shift_sort_key)
    table = pd.DataFrame(
        {shift: [" · ".join(t for _, t in sorted(cells.get((line, shift), []))) for line in lines] for shift in shifts},
        index=[f"{line_id} - {line.name}" for line_id, line in lines.items()],
    )
    st.subheader(f"{period}: {len(week.assignments)} assignments")
    st.table(table)

    # Coverage against that week's demand, if there is one.
    try:
        demands = load_demands(period, data_dir)
    except DataError:
        demands = []
    if demands:
        covered: dict[tuple[str, str, str], int] = {}
        for a in week.assignments:
            covered[(a.line, a.shift, a.role)] = covered.get((a.line, a.shift, a.role), 0) + 1
        rows = []
        for d in demands:
            for s in d.shifts:
                row = {"line": d.line, "shift": s.name}
                for role in ROLE_ORDER:
                    needed = getattr(s.staff, role)
                    row[role] = f"{covered.get((d.line, s.name, role), 0)} / {needed}" if needed else "-"
                rows.append(row)
        st.write("Coverage (covered / needed):")
        st.dataframe(pd.DataFrame(rows), hide_index=True)

    with st.expander("All assignments, with each operator's level on the line"):
        st.dataframe(pd.DataFrame([{
            "operator": a.operator,
            "name": operators[a.operator].name if a.operator in operators else "?",
            "line": a.line, "shift": a.shift, "role (slot)": a.role,
            "level on the line": operators[a.operator].lines.get(a.line, "no training") if a.operator in operators else "?",
        } for a in week.assignments]), hide_index=True)


def data_screen(data_dir: Path) -> None:
    st.header("Data")
    try:
        lines = load_lines(data_dir)
        operators = load_operators(data_dir)
    except (DataError, FileNotFoundError) as error:
        st.error(str(error))
        return

    tab_operators, tab_lines, tab_week = st.tabs(["Operators", "Lines", "Weekly data"])

    with tab_operators:
        st.write(f"{len(operators)} operators. Level on each line (empty: no training, assistant only).")
        st.dataframe(pd.DataFrame([
            {"id": o.id, "name": o.name, **{line_id: o.lines.get(line_id, "") for line_id in lines}}
            for o in operators.values()]), hide_index=True)

    with tab_lines:
        st.dataframe(pd.DataFrame([{
            "id": line.id, "name": line.name,
            "restricted group": line.restricted_group.id if line.restricted_group else "",
            "max consecutive weeks": line.restricted_group.max_consecutive_weeks if line.restricted_group else None,
            "min rest weeks": line.restricted_group.min_rest_weeks if line.restricted_group else None,
        } for line in lines.values()]), hide_index=True)

    with tab_week:
        weeks = source_weeks(data_dir)
        if not weeks:
            st.info("No weekly data.")
            return
        period = st.selectbox("Week", weeks, key="data-week")
        data = load_planning_input(period, data_dir)
        st.subheader("Demand")
        st.dataframe(pd.DataFrame([
            {"line": d.line, "shift": s.name, **{role: getattr(s.staff, role) for role in ROLE_ORDER}}
            for d in data.demands for s in d.shifts]), hide_index=True)
        st.subheader("Availability")
        rows = []
        for o in operators.values():
            availability = data.availabilities.get(o.id)
            shifts = availability.shifts if availability else []
            rows.append({"id": o.id, "name": o.name, "shifts": ", ".join(shifts) or "not available"})
        absent = sum(1 for r in rows if r["shifts"] == "not available")
        st.write(f"{len(rows) - absent} available, {absent} not available.")
        st.dataframe(pd.DataFrame(rows), hide_index=True)


def graph_screen(data_dir: Path) -> None:
    st.header("Bipartite graph")
    st.write("The graph of one week, limited to a few lines and shifts so it can be read. "
             "Operators on the left, slots on the right; the edges of the matching are highlighted.")

    weeks = source_weeks(data_dir)
    if not weeks:
        st.info("No weekly data.")
        return
    period = st.selectbox("Week", weeks, key="graph-week")
    data = load_planning_input(period, data_dir)

    all_lines = [d.line for d in data.demands]
    all_shifts = sorted({s.name for d in data.demands for s in d.shifts}, key=shift_sort_key)
    c1, c2 = st.columns(2)
    chosen_lines = c1.multiselect("Lines", all_lines, default=all_lines[:1])
    chosen_shifts = c2.multiselect("Shifts", all_shifts, default=all_shifts[:1])
    maximize = st.checkbox("Maximize the number of covered slots", value=True)
    only_candidates = st.checkbox("Hide operators with no edge", value=True)
    with st.expander("Edge weights"):
        weights = weights_form("graph")

    # Keep only the chosen lines and shifts.
    demands = []
    for d in data.demands:
        if d.line in chosen_lines:
            shifts = [s for s in d.shifts if s.name in chosen_shifts]
            if shifts:
                demands.append(replace(d, shifts=shifts))
    if not demands:
        st.info("Choose at least one line and one shift that run this week.")
        return

    graph = build_graph(replace(data, demands=demands), weights)
    if only_candidates:
        graph.remove_nodes_from([n for n, side in list(graph.nodes(data="bipartite")) if side == 0 and graph.degree(n) == 0])
    matching = find_matching(graph, maximize)

    operators = [n for n, side in graph.nodes(data="bipartite") if side == 0]
    slots = [n for n, side in graph.nodes(data="bipartite") if side == 1]
    # Both columns span the same height, so the slots are spread out even when
    # there are many more operators than slots.
    span = max(len(operators), len(slots)) - 1 or 1

    def column(nodes, x):
        step = span / (len(nodes) - 1) if len(nodes) > 1 else 0
        start = 0 if len(nodes) > 1 else -span / 2
        return {n: (x, start - i * step) for i, n in enumerate(nodes)}

    position = {**column(operators, 0), **column(slots, 1)}
    chosen = {frozenset(pair) for pair in matching.items()}

    height = max(4, 0.35 * max(len(operators), len(slots)))
    fig, ax = plt.subplots(figsize=(9, height))
    for u, v, weight in graph.edges(data="weight"):
        (x1, y1), (x2, y2) = position[u], position[v]
        if frozenset((u, v)) in chosen:
            ax.plot([x1, x2], [y1, y2], color="#d62728", linewidth=2.2, zorder=2)
            ax.text(0.5 * (x1 + x2), 0.5 * (y1 + y2), f"{weight:g}", color="#d62728", fontsize=7,
                    ha="center", va="center", backgroundcolor="white", zorder=3)
        else:
            ax.plot([x1, x2], [y1, y2], color="#bbbbbb", linewidth=0.6, zorder=1)
    for n in operators:
        x, y = position[n]
        ax.scatter(x, y, s=60, color="#1f77b4", zorder=4)
        ax.text(x - 0.03, y, n, ha="right", va="center", fontsize=8)
    for n in slots:
        x, y = position[n]
        ax.scatter(x, y, s=60, color="#2ca02c" if n in matching else "#7f7f7f", marker="s", zorder=4)
        ax.text(x + 0.03, y, n, ha="left", va="center", fontsize=8)
    ax.set_xlim(-0.45, 1.75)
    ax.axis("off")
    st.pyplot(fig)

    st.caption(f"{len(operators)} operators, {len(slots)} slots, {graph.number_of_edges()} edges; "
               f"{len(matching)} slots covered, total weight "
               f"{sum(graph[s][o]['weight'] for s, o in matching.items()):g}. "
               "This matching only uses the chosen lines and shifts, so it can differ from the full week's plan.")


# --- App -----------------------------------------------------------------------

SCREENS = {"Plan": plan_screen, "Schedule": schedule_screen, "Data": data_screen, "Graph": graph_screen}


def main() -> None:
    st.set_page_config(page_title="ShiftPlanner", layout="wide")
    st.sidebar.title("ShiftPlanner")
    screen = st.sidebar.radio("Screen", list(SCREENS))
    data_dir = Path(st.sidebar.text_input("Data folder", value="data"))
    if not (data_dir / "source").exists():
        st.error(f"No data in {data_dir / 'source'}. Copy the sample data first "
                 f"(the contents of sample_data/ into {data_dir}/) or choose another data folder.")
        return
    SCREENS[screen](data_dir)


main()
