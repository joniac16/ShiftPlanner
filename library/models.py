"""Data models: Operator, Line, Shift, Staff and Restrictions."""

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
class Restrictions:
    """Optional limits on how long an operator can stay on a line.

    After working `max_consecutive_weeks` weeks in a row on the line (any shift,
    any role), the operator must stay off it for at least `min_rest_weeks` weeks.
    None means no limit.
    """

    max_consecutive_weeks: int | None = None
    min_rest_weeks: int | None = None


@dataclass
class Line:
    id: str
    name: str
    shifts: list[Shift] = field(default_factory=list)
    restrictions: Restrictions = field(default_factory=Restrictions)
