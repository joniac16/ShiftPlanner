"""Data models: Operator, Line and Shift."""

from dataclasses import dataclass, field


@dataclass
class Shift:
    name: str  # e.g. "Morning", "Afternoon", "Night"


@dataclass
class Operator:
    id: str
    name: str
    enabled_lines: list[str] = field(default_factory=list)


@dataclass
class Line:
    id: str
    name: str
    staff_per_shift: int
