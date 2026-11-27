"""Reading of the JSON files: what goes into the algorithm (writing is in writer.py).

Every function takes the data folder as a parameter (`data` by default), so
tests can use their own dummy data with the same layout:

    <data_dir>/source/lines.json, operators.json, demands.json, availabilities.json
    <data_dir>/history/<period>.json
"""

import json
from pathlib import Path

from library.models import (
    Assignment,
    Availability,
    Line,
    LineDemand,
    Operator,
    PlanningInput,
    RestrictedGroup,
    Shift,
    Staff,
    WeekAllocation,
)
from library.utils import iso_week_to_date, sort_iso_weeks

DEFAULT_DATA_DIR = Path("data")

TRAINED_ROLES = ("specialist", "qualified")
ROLES = ("specialist", "qualified", "assistant")


class DataError(ValueError):
    """The data files are malformed or inconsistent."""


def load_lines(data_dir: Path | str = DEFAULT_DATA_DIR) -> dict[str, Line]:
    """Read source/lines.json and return a dict: line id -> Line.

    Raises DataError if a line id is repeated, or if two lines of the same
    restricted group declare different limits.
    """
    path = Path(data_dir) / "source" / "lines.json"
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    lines: dict[str, Line] = {}
    groups: dict[str, RestrictedGroup] = {}

    for item in raw:
        line_id = item["id"]
        if line_id in lines:
            raise DataError(f"Duplicate line id '{line_id}' in {path}")

        group = None
        if "restricted_group" in item:
            group = RestrictedGroup(**item["restricted_group"])
            if group.id in groups and groups[group.id] != group:
                raise DataError(
                    f"Restricted group '{group.id}' has different limits on line {line_id} "
                    f"than on other lines of the group"
                )
            groups[group.id] = group

        lines[line_id] = Line(id=line_id, name=item["name"], restricted_group=group)

    return lines


def load_operators(data_dir: Path | str = DEFAULT_DATA_DIR) -> dict[str, Operator]:
    """Read source/operators.json and return a dict: operator id -> Operator.

    Raises DataError if an operator id is repeated, or if a training level is
    not "specialist" or "qualified".
    """
    path = Path(data_dir) / "source" / "operators.json"
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    operators: dict[str, Operator] = {}

    for item in raw:
        operator_id = item["id"]
        if operator_id in operators:
            raise DataError(f"Duplicate operator id '{operator_id}' in {path}")

        training = item.get("lines", {})
        for line_id, level in training.items():
            if level not in TRAINED_ROLES:
                raise DataError(f"Operator {operator_id} has invalid level '{level}' on line {line_id}")

        operators[operator_id] = Operator(id=operator_id, name=item["name"], lines=training)

    return operators


def load_demands(period: str, data_dir: Path | str = DEFAULT_DATA_DIR) -> list[LineDemand]:
    """Read the demand of one week from source/demands.json.

    Raises DataError if the week is not in the file, a line appears twice, or a
    role in `staff` is not valid.
    """
    path = Path(data_dir) / "source" / "demands.json"
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    if period not in raw:
        raise DataError(f"Period '{period}' not found in {path}")

    demands: list[LineDemand] = []
    seen_lines: set[str] = set()

    for item in raw[period]:
        line_id = item["line"]
        if line_id in seen_lines:
            raise DataError(f"Line {line_id} appears twice in {period} in {path}")
        seen_lines.add(line_id)

        shifts = []
        for s in item["shifts"]:
            unknown = set(s["staff"]) - set(ROLES)
            if unknown:
                raise DataError(f"Unknown role(s) {sorted(unknown)} in {period}, line {line_id}, shift {s['name']}")
            shifts.append(Shift(name=s["name"], staff=Staff(**s["staff"])))

        demands.append(LineDemand(line=line_id, shifts=shifts))

    return demands


def load_availabilities(period: str, data_dir: Path | str = DEFAULT_DATA_DIR) -> dict[str, Availability]:
    """Read the availability of one week from source/availabilities.json.

    Returns a dict: operator id -> Availability. Operators not listed are not
    available that week. Raises DataError if the week is not in the file or an
    operator appears twice.
    """
    path = Path(data_dir) / "source" / "availabilities.json"
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    if period not in raw:
        raise DataError(f"Period '{period}' not found in {path}")

    availabilities: dict[str, Availability] = {}

    for item in raw[period]:
        operator_id = item["operator"]
        if operator_id in availabilities:
            raise DataError(f"Operator {operator_id} appears twice in {period} in {path}")
        availabilities[operator_id] = Availability(operator=operator_id, shifts=item["shifts"])

    return availabilities


def load_history(data_dir: Path | str = DEFAULT_DATA_DIR) -> list[WeekAllocation]:
    """Read every planned week in history/, in chronological order.

    Returns an empty list if there are no weeks. Raises DataError if a file's
    name does not match the period inside it, or a role is not valid.
    """
    folder = Path(data_dir) / "history"
    files = {path.stem: path for path in folder.glob("*.json")}

    history: list[WeekAllocation] = []

    for period in sort_iso_weeks(list(files)):
        path = files[period]
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        if raw["period"] != period:
            raise DataError(f"File {path} contains period '{raw['period']}', expected '{period}'")

        assignments = []
        for a in raw["assignments"]:
            if a["role"] not in ROLES:
                raise DataError(f"Invalid role '{a['role']}' for operator {a['operator']} in {path}")
            assignments.append(Assignment(operator=a["operator"], line=a["line"], shift=a["shift"], role=a["role"]))

        history.append(WeekAllocation(period=period, assignments=assignments))

    return history


def load_planning_input(period: str, data_dir: Path | str = DEFAULT_DATA_DIR) -> PlanningInput:
    """Load everything the solver needs to plan one week.

    Calls the five load functions above, keeps only the history weeks before
    `period`, and checks that the files fit together. Raises DataError if:
      - an operator is trained on a line that does not exist,
      - the week's demand refers to a line that does not exist,
      - the week's availability refers to an operator that does not exist.
    """
    lines = load_lines(data_dir)
    operators = load_operators(data_dir)
    demands = load_demands(period, data_dir)
    availabilities = load_availabilities(period, data_dir)

    start = iso_week_to_date(period)
    history = [week for week in load_history(data_dir) if iso_week_to_date(week.period) < start]

    for operator in operators.values():
        for line_id in operator.lines:
            if line_id not in lines:
                raise DataError(f"Operator {operator.id} is trained on line {line_id}, which does not exist")

    for demand in demands:
        if demand.line not in lines:
            raise DataError(f"Demand for {period} refers to line {demand.line}, which does not exist")

    for operator_id in availabilities:
        if operator_id not in operators:
            raise DataError(f"Availability for {period} refers to operator {operator_id}, which does not exist")

    return PlanningInput(
        period=period,
        lines=lines,
        operators=operators,
        demands=demands,
        availabilities=availabilities,
        history=history,
    )
