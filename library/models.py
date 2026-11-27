"""Data models.

Master data (data/source): Line, RestrictedGroup, Operator.
Weekly data (data/source/weeks/<period>): LineDemand, Shift, Staff, Availability.
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
