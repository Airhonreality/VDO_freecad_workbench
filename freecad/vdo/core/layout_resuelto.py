"""Tipos de salida de la resolución de vanos (ResolvedTrack, ResolvedCell, PanelPiece,
ResolvedLayout)."""

from collections.abc import Iterable, Iterator
from typing import Any

from freecad.vdo.core.layout_modelo import EPS, Cell, Track


# =====================================================================
# Resolución
# =====================================================================
class ResolvedTrack:
    track: Track
    id: str
    fixed: float | None
    start: float
    size: float
    clear_start: float
    clear_size: float
    extra_izq: float
    extra_der: float
    overflow: float

    def __init__(self, track: Track, start: float, size: float,
                 overflow: float = 0.0,
                 clear_start: float | None = None, clear_size: float | None = None,
                 extra_izq: float = 0.0, extra_der: float = 0.0) -> None:
        self.track = track
        self.id = track.id
        self.fixed = track.fixed
        self.start = float(start)
        self.size = float(max(0.0, size))
        self.clear_start = float(
            start if clear_start is None else clear_start)
        self.clear_size = float(max(0.0, (
            size if clear_size is None else clear_size)))
        self.extra_izq = float(max(0.0, extra_izq))
        self.extra_der = float(max(0.0, extra_der))
        self.overflow = float(max(0.0, overflow))

    @property
    def end(self) -> float:
        return self.start + self.size

    def __repr__(self) -> str:
        return (f"ResolvedTrack({self.id}, start={self.start:.1f}, "
                f"size={self.size:.1f}, clear={self.clear_size:.1f}, "
                f"overflow={self.overflow:.1f})")


class ResolvedCell:
    cell: Cell
    x: float
    z: float
    w: float
    h: float
    nominal_x: float
    nominal_z: float
    nominal_w: float
    nominal_h: float
    level: int
    children: list["ResolvedCell"]

    def __init__(self, cell: Cell, x: float, z: float, w: float, h: float,
                 level: int = 0,
                 nominal_x: float | None = None, nominal_z: float | None = None,
                 nominal_w: float | None = None, nominal_h: float | None = None) -> None:
        self.cell = cell
        self.x = float(x)
        self.z = float(z)
        self.w = float(max(0.0, w))
        self.h = float(max(0.0, h))
        self.nominal_x = float(x if nominal_x is None else nominal_x)
        self.nominal_z = float(z if nominal_z is None else nominal_z)
        self.nominal_w = float(max(
            0.0, w if nominal_w is None else nominal_w))
        self.nominal_h = float(max(
            0.0, h if nominal_h is None else nominal_h))
        self.level = int(level)
        self.children = []

    @property
    def label(self) -> str:
        return self.cell.label

    @property
    def rect(self) -> tuple[float, float, float, float]:
        return (self.x, self.z, self.w, self.h)

    def walk(self) -> Iterator["ResolvedCell"]:
        yield self
        for child in self.children:
            yield from child.walk()

    def __repr__(self) -> str:
        return (f"ResolvedCell({self.label}, x={self.x:.1f}, z={self.z:.1f}, "
                f"w={self.w:.1f}, h={self.h:.1f})")


class PanelPiece:
    """Panel interno resuelto en coordenadas locales del COCO."""

    axis: str
    role: str
    path: str
    x: float
    z: float
    w: float
    h: float
    thickness: float
    nombre: str

    def __init__(self, axis: str, role: str, path: str, x: float, z: float,
                 w: float, h: float, thickness: float,
                 nombre: str | None = None) -> None:
        self.axis = axis
        self.role = role
        self.path = path
        self.x = float(x)
        self.z = float(z)
        self.w = float(max(0.0, w))
        self.h = float(max(0.0, h))
        self.thickness = float(max(0.0, thickness))
        self.nombre = nombre or f"Division_{axis}_{path}"

    def __repr__(self) -> str:
        return (f"PanelPiece({self.nombre}, {self.axis}, "
                f"x={self.x:.1f}, z={self.z:.1f}, "
                f"w={self.w:.1f}, h={self.h:.1f})")


class ResolvedLayout:
    inner_w: float
    inner_h: float
    thickness: float
    columns: list[ResolvedTrack]
    rows: list[ResolvedTrack]
    cells: list[ResolvedCell]
    pieces: list[PanelPiece]
    warnings: list[str]
    overflow: bool
    tiras: list[dict[str, Any]]

    def __init__(self, inner_w: float, inner_h: float, thickness: float,
                 columns: list[ResolvedTrack], rows: list[ResolvedTrack],
                 cells: list[ResolvedCell], pieces: list[PanelPiece],
                 warnings: Iterable[str]) -> None:
        self.inner_w = float(inner_w)
        self.inner_h = float(inner_h)
        self.thickness = float(thickness)
        self.columns = columns
        self.rows = rows
        self.cells = cells
        self.pieces = pieces
        self.warnings = list(warnings)
        # D-84: tiras de division asignadas despues por coco_spaces.py; antes no se declaraban.
        self.tiras: list[dict[str, Any]] = []
        self.overflow = (
            any(c.overflow > EPS for c in columns)
            or any(r.overflow > EPS for r in rows)
            or any("no cabe" in w.lower() or "excede" in w.lower()
                   for w in warnings)
        )

    def walk_cells(self) -> Iterator[ResolvedCell]:
        for cell in self.cells:
            yield from cell.walk()

    def summary(self) -> str:
        lineas = [
            f"Matriz {len(self.columns)} × {len(self.rows)}",  # noqa: RUF001 - etiqueta de interfaz: signo tipografico visible (x o -) que el usuario ve; cambiarlo altera el texto
            f"Interior: {self.inner_w:.1f} × {self.inner_h:.1f} mm",  # noqa: RUF001 - etiqueta de interfaz: signo tipografico visible (x o -) que el usuario ve; cambiarlo altera el texto
            f"Paneles internos: {len(self.pieces)}",
        ]
        if self.overflow:
            lineas.append("⚠ Hay medidas que no caben.")
        for warning in self.warnings:
            lineas.append("⚠ " + warning)
        return "\n".join(lineas)
