"""Modelos de datos: Operario, Linea y Turno."""

from dataclasses import dataclass, field


@dataclass
class Turno:
    nombre: str  # p. ej. "Mañana", "Tarde", "Noche"


@dataclass
class Operario:
    id: str
    nombre: str
    lineas_habilitadas: list[str] = field(default_factory=list)


@dataclass
class Linea:
    id: str
    nombre: str
    personal_por_turno: int
