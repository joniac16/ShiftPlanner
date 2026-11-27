"""Data models: Operator, Line, Shift, Staff and RestrictedGroup."""

from dataclasses import dataclass, field


@dataclass
class Staff:
    """Number of operators of each type required in a shift."""

    specialist: int = 0
    qualified: int = 0
    assistant: int = 0


@dataclass
class Shift:
    name: str  # e.g. "Morning", "Afternoon", "Night", "Weekend"
    staff: Staff = field(default_factory=Staff)


@dataclass
class Operator:
    id: str
    name: str
    shifts: list[str] = field(default_factory=list)  # shift names the operator can cover
    lines: dict[str, str] = field(default_factory=dict)  # line id -> "specialist" | "qualified"
    # Lines not listed in `lines` can only be covered as "assistant".


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
    shifts: list[Shift] = field(default_factory=list)
    restricted_group: RestrictedGroup | None = None  # None: no restrictions
