"""Matriz de vanos (Layout): construcción, edición, serialización y migración legacy."""

import json
import logging
from collections.abc import Iterable, Iterator, Mapping
from typing import Any

from freecad.vdo.core.layout_modelo import (
    AXIS_X,
    AXIS_Y,
    VERSION,
    Cell,
    LayoutError,
    Track,
    _id_unico,
    _sufijo_id,
    _to_float,
)

_LOG = logging.getLogger(__name__)


class Layout:
    """Matriz raíz de columnas/filas con contenido anidado por celda."""

    columns: list[Track]
    rows: list[Track]
    cells: dict[str, Cell]

    # Any: acepta Track, str o dict (migración); el tipo real se normaliza abajo.
    def __init__(self, columns: Iterable[Any] | None = None,
                 rows: Iterable[Any] | None = None,
                 cells: Mapping[str, Any] | None = None) -> None:
        self.columns = list(columns or [Track("x1")])
        self.rows = list(rows or [Track("y1")])
        self.cells = dict(cells or {})
        self._normalizar()

    # -----------------------------------------------------------------
    # Normalización / serialización
    # -----------------------------------------------------------------
    @staticmethod
    def key(col_id: str, row_id: str) -> str:
        return f"{col_id}|{row_id}"

    def _normalizar(self) -> None:  # noqa: C901 - complejidad 14 (max 12): funcion con ramas por caso; dividirla cambia el flujo sin golden por rama (D-81)
        if not self.columns:
            self.columns = [Track("x1")]
        if not self.rows:
            self.rows = [Track("y1")]

        vistos: set[str] = set()
        columnas: list[Track] = []
        for i, col in enumerate(self.columns):
            if isinstance(col, str):
                col = Track(col)
            elif isinstance(col, dict):
                col = Track.from_dict(col, "x", i)
            if col.id in vistos:
                col.id = _id_unico("x", vistos)
            vistos.add(col.id)
            columnas.append(col)
        self.columns = columnas

        vistos = set()
        filas: list[Track] = []
        for i, row in enumerate(self.rows):
            if isinstance(row, str):
                row = Track(row)
            elif isinstance(row, dict):
                row = Track.from_dict(row, "y", i)
            if row.id in vistos:
                row.id = _id_unico("y", vistos)
            vistos.add(row.id)
            filas.append(row)
        self.rows = filas

        nuevas: dict[str, Cell] = {}
        for col in self.columns:
            for row in self.rows:
                k = self.key(col.id, row.id)
                cell = self.cells.get(k)
                if not isinstance(cell, Cell):
                    cell = Cell.from_dict(cell or {})
                    cell.px = _sufijo_id(col.id, "x")
                    cell.py = _sufijo_id(row.id, "y")
                    cell.fixed = None
                nuevas[k] = cell
        self.cells = nuevas

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": VERSION,
            "columns": [c.to_dict() for c in self.columns],
            "rows": [r.to_dict() for r in self.rows],
            "cells": {
                k: cell.to_dict()
                for k, cell in self.cells.items()
            },
        }

    def dumps(self) -> str:
        return json.dumps(
            self.to_dict(), ensure_ascii=False, separators=(",", ":"))

    @classmethod
    def from_dict(cls, data: Any) -> "Layout":  # Any: dict de JSON, sin esquema fijo
        if not isinstance(data, dict):
            return cls()
        columns = [
            Track.from_dict(c, "x", i)
            for i, c in enumerate(data.get("columns", []))
        ] or [Track("x1")]
        rows = [
            Track.from_dict(r, "y", i)
            for i, r in enumerate(data.get("rows", []))
        ] or [Track("y1")]

        cells: dict[str, Cell] = {}
        raw_cells = data.get("cells", {})
        if isinstance(raw_cells, dict):
            for k, value in raw_cells.items():
                cells[k] = Cell.from_dict(value)
        elif isinstance(raw_cells, list):
            for i, value in enumerate(raw_cells):
                if not isinstance(value, dict):
                    continue
                cell = Cell.from_dict(value)
                if i < len(columns) * len(rows):
                    col = columns[i % len(columns)]
                    row = rows[i // len(columns)]
                    cells[cls.key(col.id, row.id)] = cell
        return cls(columns=columns, rows=rows, cells=cells)

    @classmethod
    def loads(cls, texto: str | None) -> "Layout":
        if not texto or not str(texto).strip():
            return cls()
        try:
            data = json.loads(texto)
            return cls.from_dict(data)
        except (TypeError, ValueError, KeyError, AttributeError) as exc:
            _LOG.warning("layout_matriz: datos no validos, usa matriz por defecto: %s", exc)
            return cls()

    def copy(self) -> "Layout":
        return Layout.from_dict(self.to_dict())

    # -----------------------------------------------------------------
    # Matriz raíz
    # -----------------------------------------------------------------
    def add_column(self, fixed: object = None) -> Track:
        col = Track(_id_unico("x", [c.id for c in self.columns]), fixed)
        self.columns.append(col)
        for row in self.rows:
            self.cells[self.key(col.id, row.id)] = Cell(
                px=_sufijo_id(col.id, "x"),
                py=_sufijo_id(row.id, "y"),
            )
        return col

    def add_row(self, fixed: object = None) -> Track:
        row = Track(_id_unico("y", [r.id for r in self.rows]), fixed)
        self.rows.append(row)
        for col in self.columns:
            self.cells[self.key(col.id, row.id)] = Cell(
                px=_sufijo_id(col.id, "x"),
                py=_sufijo_id(row.id, "y"),
            )
        return row

    def set_column_fixed(self, index: int, fixed: object) -> None:
        if 0 <= index < len(self.columns):
            self.columns[index].fixed = _to_float(fixed)

    def set_row_fixed(self, index: int, fixed: object) -> None:
        if 0 <= index < len(self.rows):
            self.rows[index].fixed = _to_float(fixed)

    def get_cell(self, col_index: int, row_index: int) -> Cell | None:
        if not (0 <= col_index < len(self.columns)
                and 0 <= row_index < len(self.rows)):
            return None
        col = self.columns[col_index]
        row = self.rows[row_index]
        return self.cells.get(self.key(col.id, row.id))

    def _celdas_arbol(self, cell: Cell) -> Iterator[Cell]:
        yield cell
        for child in getattr(cell, "children", []):
            yield from self._celdas_arbol(child)

    # -----------------------------------------------------------------
    # Subdivisiones anidadas
    # -----------------------------------------------------------------
    @staticmethod
    def _etiquetas_hijos(cell: Cell, axis: str, count: int) -> list[tuple[str, str]]:
        if axis == AXIS_X:
            return [(f"{cell.px}.{k + 1}", cell.py) for k in range(count)]
        return [(cell.px, f"{cell.py}.{k + 1}") for k in range(count)]

    def set_split(self, cell: Cell | None, axis: str, count: int | str) -> bool:
        if cell is None:
            return False
        if axis not in (AXIS_X, AXIS_Y):
            raise LayoutError("Eje de subdivisión inválido.")
        count = int(count)
        if count < 2 or count > 100:
            raise LayoutError("N debe estar entre 2 y 100.")
        if not (0 <= count <= 100):
            raise LayoutError("N inválido.")

        etiquetas = self._etiquetas_hijos(cell, axis, count)
        viejos = list(cell.children or [])
        mismo_eje = cell.axis == axis
        nuevos: list[Cell] = []
        for k, (px, py) in enumerate(etiquetas):
            if mismo_eje and k < len(viejos):
                child = viejos[k]
                child.px = px
                child.py = py
                nuevos.append(child)
            else:
                nuevos.append(Cell(px=px, py=py))
        cell.axis = axis
        cell.children = nuevos
        return True

    def disable_split(self, cell: Cell | None) -> bool:
        if cell is None:
            return False
        cell.axis = None
        cell.children = []
        return True

    def set_cell_fixed(self, cell: Cell | None, fixed: object) -> None:
        if cell is not None:
            cell.fixed = _to_float(fixed)

    def iter_all(self) -> Iterator[Cell]:
        for cell in self.cells.values():
            yield from self._celdas_arbol(cell)

    def find_label(self, label: str) -> Cell | None:
        for cell in self.iter_all():
            if cell.label == label:
                return cell
        return None

    # -----------------------------------------------------------------
    # Migración desde EspaciosX / EspaciosY
    # -----------------------------------------------------------------
    @classmethod
    def from_legacy(cls, espacios_x: str = "", espacios_y: str = "") -> tuple["Layout", list[str]]:
        warnings: list[str] = []
        cols = _legacy_tracks(espacios_x, "X", warnings)
        rows = _legacy_tracks(espacios_y, "Y", warnings)
        layout = cls(columns=cols, rows=rows)
        if warnings:
            warnings.insert(
                0, "Migración legacy: se conservaron las divisiones raíz; "
                   "las subdivisiones antiguas no se pudieron mapear.")
        return layout, warnings


def _legacy_tracks(texto: str, eje: str, warnings: list[str]) -> list[Track]:  # noqa: C901 - complejidad 13 (max 12): funcion con ramas por caso; dividirla cambia el flujo sin golden por rama (D-81)
    nodos: list[Any] = []
    if texto:
        try:
            data = json.loads(texto)
            if isinstance(data, list):
                nodos = data
        except (TypeError, ValueError) as exc:
            _LOG.warning("layout_matriz: JSON legacy de eje invalido: %s", exc)
            warnings.append(f"JSON legacy de {eje} inválido.")

    tracks: list[Track] = []
    for nodo in nodos:
        if not isinstance(nodo, dict):
            continue
        tipo = nodo.get("type", "fijo")
        if tipo == "iguales":
            count = max(1, int(nodo.get("count", 1) or 1))
            for _ in range(count):
                tracks.append(Track(f"_{len(tracks) + 1}", None))
            if nodo.get("children"):
                warnings.append(
                    f"{eje}: sub-árbol dentro de 'iguales' no migrado.")
        elif tipo == "fijo":
            tracks.append(Track(f"_{len(tracks) + 1}",
                                nodo.get("value", 0.0)))
        else:
            tracks.append(Track(f"_{len(tracks) + 1}", None))
        if nodo.get("children"):
            warnings.append(
                f"{eje}: sub-árbol de {nodo.get('id', '?')} no migrado.")

    prefijo = "x" if eje == "X" else "y"
    if not tracks:
        tracks = [Track(f"{prefijo}1", None)]
    else:
        for i, track in enumerate(tracks):
            track.id = f"{prefijo}{i + 1}"
    return tracks
