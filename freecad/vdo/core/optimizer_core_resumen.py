"""Resumen agregado y texto-resumen del optimizador de corte 2D.
Extraido de optimizer_core.py (M7, D-86)."""

from typing import Any

from freecad.vdo.core.optimizer_core import MIN_OFFCUT


def _retal_area(sheet: dict[str, Any], min_side: float = MIN_OFFCUT) -> float:
    total: float = sum(o["w"] * o["h"] for o in sheet.get("offcuts", [])
               if min(o["w"], o["h"]) >= min_side)
    return total


def resumen_global(groups: list[dict[str, Any]], board_w: float,
                   board_h: float) -> dict[str, Any]:
    """Totales agregados de todos los grupos (para la barra de estado)."""
    n_total = sum(g["n_pieces"] for g in groups)
    n_unplaced = sum(len(g["unplaced"]) for g in groups)
    n_placed = n_total - n_unplaced
    n_boards = sum(len(g["sheets"]) for g in groups)

    used = sum(s["used_area"] for g in groups for s in g["sheets"])
    board_area = board_w * board_h * n_boards if n_boards else 0.0
    retal = sum(_retal_area(s) for g in groups for s in g["sheets"])
    eff = (used / board_area * 100.0) if board_area else 0.0

    return {
        "n_total": n_total,
        "n_placed": n_placed,
        "n_unplaced": n_unplaced,
        "n_boards": n_boards,
        "used_area_m2": used / 1e6,
        "board_area_m2": board_area / 1e6,
        "retal_m2": retal / 1e6,
        "waste_m2": (board_area - used) / 1e6,
        "efficiency": eff,
    }


def resumen(sheets: list[dict[str, Any]], unplaced: list[dict[str, Any]]) -> str:
    """Devuelve un texto-resumen legible del resultado."""
    lines: list[str] = []
    n_piezas = sum(len(s["placements"]) for s in sheets)
    lines.append(f"Tableros usados: {len(sheets)}")
    lines.append(f"Piezas colocadas: {n_piezas}")
    if sheets:
        total_eff = sum(s["efficiency"] for s in sheets) / len(sheets)
        lines.append(f"Aprovechamiento medio: {total_eff:.1f}%")
    if unplaced:
        lines.append(f"Piezas NO colocadas: {len(unplaced)}")
        for p in unplaced[:20]:
            lines.append(f"   - {p['name']} ({p['w']:.0f}x{p['h']:.0f})")
    return "\n".join(lines)
