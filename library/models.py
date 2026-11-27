"""Data models.

Master data (data/source): Line, RestrictedGroup, Operator.
Weekly data (data/source/demands.json, availabilities.json): LineDemand, Shift,
Staff, Availability.
Allocations (data/output, data/history): Assignment, WeekAllocation.
Solver input: PlanningInput.
Graph: MatchWeights.
Solver output: PlanningResult.
"""

from dataclasses import dataclass, field


# --- Master data ---------------------------------------------------------


@dataclass
class RestrictedGroup:
    """Group of lines that share a limit on consecutive weeks.

    Working on any line of the group (any shift, any role) counts as a week in
    the group. After `max_consecutive_weeks` weeks in a row in the group, the
    operator must stay off all its lines for at least `min_rest_weeks` weeks.
    Every line of the same group must declare the same values.
    """

    id: str
    max_consecutive_weeks: int
    min_rest_weeks: int


@dataclass
class Line:
    id: str
    name: str
    restricted_group: RestrictedGroup | None = None  # None: no restrictions


@dataclass
class Operator:
    id: str
    name: str
    lines: dict[str, str] = field(default_factory=dict)  # line id -> "specialist" | "qualified"
    # Lines not listed in `lines` can only be covered as "assistant".


# --- Weekly data -----------------------------------------------------------


@dataclass
class Staff:
    """Number of operators of each role required in a shift."""

    specialist: int = 0
    qualified: int = 0
    assistant: int = 0


@dataclass
class Shift:
    name: str  # "Morning", "Afternoon" or "Night"
    staff: Staff = field(default_factory=Staff)


@dataclass
class LineDemand:
    """Shifts a line runs in a given week and the staff each one needs."""

    line: str  # line id
    shifts: list[Shift] = field(default_factory=list)


@dataclass
class Availability:
    """Shifts an operator can cover in a given week (empty: not available)."""

    operator: str  # operator id
    shifts: list[str] = field(default_factory=list)


# --- Allocations -------------------------------------------------------------


@dataclass
class Assignment:
    """One operator working on a line, in a shift, with a role, for a week."""

    operator: str  # operator id
    line: str  # line id
    shift: str  # shift name
    role: str  # "specialist" | "qualified" | "assistant"


@dataclass
class WeekAllocation:
    """All the assignments of a week (a proposal in data/output or an approved week in data/history)."""

    period: str  # e.g. "2027-W5"
    assignments: list[Assignment] = field(default_factory=list)


# --- Solver input --------------------------------------------------------------


@dataclass
class PlanningInput:
    """Everything the solver needs to plan one week."""

    period: str
    lines: dict[str, Line]  # line id -> Line
    operators: dict[str, Operator]  # operator id -> Operator
    demands: list[LineDemand]  # lines running this week and their needs
    availabilities: dict[str, Availability]  # operator id -> Availability (missing: not available)
    history: list[WeekAllocation]  # approved weeks before `period`, oldest first


# --- Graph ---------------------------------------------------------------------


@dataclass
class MatchWeights:
    """Weight of an edge (operator -> slot), by the operator's level on the line
    and the role of the slot. Higher means preferred.

    The matching first covers as many slots as possible; the weights only decide
    among the matchings that cover the same number of slots. Change them to
    experiment, e.g. MatchWeights(qualified_as_specialist=0.5).
    """

    exact: float = 10  # same level as the slot (untrained operator as assistant included)
    specialist_as_qualified: float = 6
    qualified_as_assistant: float = 3  # waste of training
    specialist_as_assistant: float = 2  # waste of training
    qualified_as_specialist: float = 1  # last resort


# --- Solver output -------------------------------------------------------------


@dataclass
class PlanningResult:
    """What the solver returns for a week: the proposal and a short report.

    A proposal is always returned, even if some slots could not be covered.
    """

    allocation: WeekAllocation  # the proposal (what is saved to data/output)
    uncovered_slots: dict[str, int]  # slot id -> number of candidate operators it had
    unassigned_operators: list[str]  # available operators who got no slot
    total_weight: float  # sum of the weights of the chosen edges
