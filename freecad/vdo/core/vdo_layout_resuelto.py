"""Tipos de salida de la resolución de vanos (ResolvedTrack, ResolvedCell, PanelPiece, ResolvedLayout)."""

from freecad.vdo.core.vdo_layout_modelo import EPS


# =====================================================================
# Resolución
# =====================================================================
class ResolvedTrack:
    def __init__(self, track, start, size, overflow=0.0,
                 clear_start=None, clear_size=None,
                 extra_izq=0.0, extra_der=0.0):
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
    def end(self):
        return self.start + self.size

    @property
    def clear_end(self):
        return self.clear_start + self.clear_size

    @property
    def nominal_start(self):
        return self.start

    @property
    def nominal_size(self):
        return self.size

    def __repr__(self):
        return (f"ResolvedTrack({self.id}, start={self.start:.1f}, "
                f"size={self.size:.1f}, clear={self.clear_size:.1f}, "
                f"overflow={self.overflow:.1f})")


class ResolvedCell:
    def __init__(self, cell, x, z, w, h, level=0,
                 nominal_x=None, nominal_z=None,
                 nominal_w=None, nominal_h=None):
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
    def label(self):
        return self.cell.label

    @property
    def rect(self):
        return (self.x, self.z, self.w, self.h)

    @property
    def nominal_rect(self):
        return (self.nominal_x, self.nominal_z,
                self.nominal_w, self.nominal_h)

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def __repr__(self):
        return (f"ResolvedCell({self.label}, x={self.x:.1f}, z={self.z:.1f}, "
                f"w={self.w:.1f}, h={self.h:.1f})")


class PanelPiece:
    """Panel interno resuelto en coordenadas locales del COCO."""

    def __init__(self, axis, role, path, x, z, w, h, thickness,
                 nombre=None):
        self.axis = axis
        self.role = role
        self.path = path
        self.x = float(x)
        self.z = float(z)
        self.w = float(max(0.0, w))
        self.h = float(max(0.0, h))
        self.thickness = float(max(0.0, thickness))
        self.nombre = nombre or f"Division_{axis}_{path}"

    def __repr__(self):
        return (f"PanelPiece({self.nombre}, {self.axis}, "
                f"x={self.x:.1f}, z={self.z:.1f}, "
                f"w={self.w:.1f}, h={self.h:.1f})")


class ResolvedLayout:
    def __init__(self, inner_w, inner_h, thickness, columns, rows,
                 cells, pieces, warnings):
        self.inner_w = float(inner_w)
        self.inner_h = float(inner_h)
        self.thickness = float(thickness)
        self.columns = columns
        self.rows = rows
        self.cells = cells
        self.pieces = pieces
        self.warnings = list(warnings)
        self.overflow = (
            any(c.overflow > EPS for c in columns)
            or any(r.overflow > EPS for r in rows)
            or any("no cabe" in w.lower() or "excede" in w.lower()
                   for w in warnings)
        )

    def walk_cells(self):
        for cell in self.cells:
            yield from cell.walk()

    def total_panels(self):
        return len(self.pieces)

    def summary(self):
        lineas = [
            f"Matriz {len(self.columns)} × {len(self.rows)}",
            f"Interior: {self.inner_w:.1f} × {self.inner_h:.1f} mm",
            f"Paneles internos: {len(self.pieces)}",
        ]
        if self.overflow:
            lineas.append("⚠ Hay medidas que no caben.")
        for warning in self.warnings:
            lineas.append("⚠ " + warning)
        return "\n".join(lineas)
