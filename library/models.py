"""Data models: Operator, Line, Shift and Staff."""

from dataclasses import dataclass, field


@dataclass
class Staff:
    """Number of operators of each type required in a shift."""

    specialist: int = 0
    trained: int = 0
    assistant: int = 0


@dataclass
class Shift:
    name: str  # e.g. "Morning", "Afternoon", "Night", "Weekend"
    staff: Staff = field(default_factory=Staff)


@dataclass
class Operator:
    id: str
    name: str
    enabled_lines: list[str] = field(default_factory=list)


@dataclass
class Line:
    id: str
    name: str
    shifts: list[Shift] = field(default_factory=list)
