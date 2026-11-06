#!/usr/bin/env python3
"""
optimizer_core.py
Optimizador de corte 2D (nesting de RECTÁNGULOS) para tableros de melamina.

Agnóstico de FreeCAD: Python puro, sin dependencias externas.
Interfaz: consume la lista de corte en CSV (la que genera vdo_cutting_list)
          y produce un acomodo por tablero, listo para previsualizar.

Cubre lo esencial del taller:
  - tamaño de tablero configurable (con presets)
  - kerf (grosor de sierra)
  - margen / recorte perimetral
  - rotación de piezas (si el material tiene veta, desactivar)
  - múltiples tableros automáticos
  - reporte de aprovechamiento (%) y piezas no colocadas

Motor de empaquetado: MaxRects con heurística Best-Short-Side-Fit (BSSF).
Es determinista, rápido y exacto para piezas rectangulares.

Uso por CLI:
    python3 optimizer_core.py --csv lista.csv \
        --board 2440x1830 --kerf 4 --margin 10 --out plan.svg
    # Canteado propio: restar canto antes del kerf
    python3 optimizer_core.py --csv lista.csv --descontar-cantos

Uso programático:
    from freecad.vdo.core import optimizer_core as opt
    from freecad.vdo.core import optimizer_lista_corte as lista
    parts = lista.read_cutting_csv("lista.csv")
    sheets, unplaced = opt.optimize(
        lista.expand_pieces(parts),
        board_w=2440, board_h=1830, kerf=4, margin=10,
        allow_rotation=True, descontar_cantos=False)
"""

from collections.abc import Callable
from typing import Any

from freecad.vdo.core.optimizer_lista_corte import _medidas_corte

# ----------------------------------------------------------------------
# Presets de tablero (mm) — estándar de taller
# ----------------------------------------------------------------------
PRESETS = {
    "Estándar EN 2440x1830": (2440.0, 1830.0),
    "Medio 1220x2440":       (1220.0, 2440.0),
    "Cuadrado 1000x1000":    (1000.0, 1000.0),
    "Largo 3000x600":        (3000.0, 600.0),
    "Grande 3050x1220":      (3050.0, 1220.0),
}

KERF_DEFAULT = 4.0      # grosor de sierra típico (mm)
MARGIN_DEFAULT = 10.0   # recorte/rebaba perimetral (mm)


# ----------------------------------------------------------------------
# 2. Motor MaxRects (BSSF)
# ----------------------------------------------------------------------
def _area(r: list[float]) -> float:
    return r[2] * r[3]


def _intersects(a: list[float], b: list[float]) -> bool:
    return not (b[0] >= a[0] + a[2] or b[0] + b[2] <= a[0] or
                b[1] >= a[1] + a[3] or b[1] + b[3] <= a[1])


def _contains(outer: list[float], inner: list[float]) -> bool:
    return (inner[0] >= outer[0] and inner[1] >= outer[1] and
            inner[0] + inner[2] <= outer[0] + outer[2] + 1e-9 and
            inner[1] + inner[3] <= outer[1] + outer[3] + 1e-9)


def _prune(rects: list[list[float]]) -> list[list[float]]:
    """Elimina rectángulos libres contenidos en otro (MaxRects prune)."""
    rects = [r for r in rects if r[2] > 1e-6 and r[3] > 1e-6]
    keep: list[list[float]] = []
    for i, r in enumerate(rects):
        contained = False
        for j, s in enumerate(rects):
            if i == j:
                continue
            # Si son idénticos, conservar solo el de menor índice.
            if _contains(s, r) and (
                    _area(s) > _area(r) or (abs(_area(s) - _area(r)) < 1e-9 and j < i)):
                contained = True
                break
        if not contained:
            keep.append(r)
    return keep


def _split_free(free: list[list[float]], used: list[float]) -> list[list[float]]:
    """Divide los rectángulos libres alrededor de la pieza colocada."""
    new: list[list[float]] = []
    for fr in free:
        if not _intersects(fr, used):
            new.append(fr)
            continue
        # izquierda
        if used[0] > fr[0] + 1e-9:
            new.append([fr[0], fr[1], used[0] - fr[0], fr[3]])
        # derecha
        if used[0] + used[2] < fr[0] + fr[2] - 1e-9:
            new.append([used[0] + used[2], fr[1],
                        fr[0] + fr[2] - (used[0] + used[2]), fr[3]])
        # arriba (Y menor)
        if used[1] > fr[1] + 1e-9:
            new.append([fr[0], fr[1], fr[2], used[1] - fr[1]])
        # abajo (Y mayor)
        if used[1] + used[3] < fr[1] + fr[3] - 1e-9:
            new.append([fr[0], used[1] + used[3], fr[2],
                        fr[1] + fr[3] - (used[1] + used[3])])
    return _prune(new)


# Heurísticas de selección de hueco (menor puntuación = mejor).
#   dst_w / dst_h : sobrante a lo ancho / alto del hueco
#   free_a        : área del hueco libre
#   piece_a       : área de la pieza
_HEURISTICS = {
    "bssf": lambda dst_w, dst_h, free_a, piece_a: (min(dst_w, dst_h), max(dst_w, dst_h)),
    "blsf": lambda dst_w, dst_h, free_a, piece_a: (max(dst_w, dst_h), min(dst_w, dst_h)),
    "baf":  lambda dst_w, dst_h, free_a, piece_a: (free_a - piece_a, min(dst_w, dst_h)),
}

# Órdenes de colocación probados (de mayor a menor por esta clave).
_SORTERS = {
    "area":   lambda p: p["w"] * p["h"],
    "maxdim": lambda p: max(p["w"], p["h"]),
    "height": lambda p: p["h"],
    "width":  lambda p: p["w"],
}


def _pack_bin(bin_w: float, bin_h: float, items: list[dict[str, Any]], allow_rotation: bool,
              score_func: Callable[[float, float, float, float], tuple[float, float]],
              ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[list[float]]]:
    """Empaqueta lo que quepa en un tablero. Devuelve (placed, remaining)."""
    free: list[list[float]] = [[0.0, 0.0, float(bin_w), float(bin_h)]]
    placed: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []

    for it in items:
        # (score, x, y, w, h, rotated)
        best: tuple[tuple[float, float], float, float, float, float, bool] | None = None
        for fr in free:
            candidates = [(it["w"], it["h"], False)]
            if allow_rotation:
                candidates.append((it["h"], it["w"], True))
            for cw, ch, rot in candidates:
                if cw <= fr[2] + 1e-9 and ch <= fr[3] + 1e-9:
                    dst_w = fr[2] - cw
                    dst_h = fr[3] - ch
                    s = score_func(dst_w, dst_h, fr[2] * fr[3], cw * ch)
                    if best is None or s < best[0]:
                        best = (s, fr[0], fr[1], cw, ch, rot)

        if best is None:
            remaining.append(it)
            continue

        _, x, y, cw, ch, rot = best
        placed.append({"item": it, "x": x, "y": y,
                       "w": cw, "h": ch, "rotated": rot})
        free = _split_free(free, [x, y, cw, ch])

    return placed, remaining, free


def _pack_all(usable_w: float, usable_h: float, items: list[dict[str, Any]],
              allow_rotation: bool,
              score_func: Callable[[float, float, float, float], tuple[float, float]],
              ) -> tuple[list[list[dict[str, Any]]], list[dict[str, Any]], list[list[list[float]]]]:
    """Empaqueta en tantos tableros como haga falta con una estrategia.

    Devuelve (lista_de_tableros, pendientes). Cada tablero es una lista de
    placements crudos {"item", "x", "y", "w", "h", "rotated"}.
    """
    boards: list[list[dict[str, Any]]] = []
    frees: list[list[list[float]]] = []
    pending = items
    while pending:
        placed, remaining, free = _pack_bin(usable_w, usable_h, pending,
                                            allow_rotation, score_func)
        if not placed:
            break
        boards.append(placed)
        frees.append(free)
        pending = remaining
    return boards, pending, frees


# ----------------------------------------------------------------------
# 3. Optimización completa (múltiples tableros)
# ----------------------------------------------------------------------
def _validar_tablero(board_w: float, board_h: float, margin: float) -> tuple[float, float]:
    """Devuelve las dimensiones utiles del tablero; rechaza margen excesivo."""
    usable_w = board_w - 2 * margin
    usable_h = board_h - 2 * margin
    if usable_w <= 0 or usable_h <= 0:
        raise ValueError("El margen es mayor que el tablero.")
    return usable_w, usable_h


def _inflar_piezas(pieces: list[dict[str, Any]], kerf: float,
                   descontar_cantos: bool) -> list[dict[str, Any]]:
    """Infla cada pieza por el kerf: garantiza separacion de corte."""
    inflated: list[dict[str, Any]] = []
    for p in pieces:
        w, h = _medidas_corte(p, descontar_cantos)
        inflated.append({"name": p["name"], "material": p["material"],
                         "thickness": p.get("thickness"),
                         "w": w + kerf, "h": h + kerf})
    return inflated


def _mejor_empaquetado(usable_w: float, usable_h: float, inflated: list[dict[str, Any]],
                       allow_rotation: bool,
                       ) -> tuple[list[list[dict[str, Any]]], list[dict[str, Any]],
           list[list[list[float]]]]:
    """Prueba heuristica x orden y devuelve (boards, pending, frees) del mejor."""
    best: tuple[tuple[int, float], list[list[dict[str, Any]]], list[dict[str, Any]],
                list[list[list[float]]]] | None = None
    for _hname, score_func in _HEURISTICS.items():
        for _sname, skey in _SORTERS.items():
            ordered = sorted(inflated, key=skey, reverse=True)
            boards, pending, frees = _pack_all(usable_w, usable_h, ordered,
                                               allow_rotation, score_func)
            placed_area = sum(pl["w"] * pl["h"] for b in boards for pl in b)
            key = (len(boards) if boards else 10 ** 9, -placed_area)
            if best is None or key < best[0]:
                best = (key, boards, pending, frees)
    assert best is not None  # _HEURISTICS y _SORTERS no vacíos: el bucle siempre asigna
    return best[1], best[2], best[3]


def _placements_tablero(placed: list[dict[str, Any]], margin: float,
                        kerf: float) -> list[dict[str, Any]]:
    """Piezas colocadas en un tablero, con coordenadas reales del tablero."""
    placements: list[dict[str, Any]] = []
    for pl in placed:
        it = pl["item"]
        placements.append({
            "name": it["name"],
            "material": it["material"],
            "thickness": it["thickness"],
            "x": pl["x"] + margin,
            "y": pl["y"] + margin,
            "w": it["w"] - kerf,
            "h": it["h"] - kerf,
            "rotated": pl["rotated"],
        })
    return placements


def _retales_tablero(frees: list[list[float]], margin: float) -> list[dict[str, Any]]:
    """Rectangulos libres del tablero (sobrante reutilizable) en mm reales."""
    offcuts: list[dict[str, Any]] = []
    for fr in frees:
        if fr[2] > 1e-6 and fr[3] > 1e-6:
            offcuts.append({
                "x": fr[0] + margin,
                "y": fr[1] + margin,
                "w": fr[2],
                "h": fr[3],
            })
    return offcuts


def _hoja_tablero(idx: int, board_w: float, board_h: float,
                  placements: list[dict[str, Any]],
                  offcuts: list[dict[str, Any]]) -> dict[str, Any]:
    """Dict de salida de un tablero con su eficiencia."""
    board_area = board_w * board_h
    used = sum(pl["w"] * pl["h"] for pl in placements)
    return {
        "index": idx + 1,
        "board_w": board_w,
        "board_h": board_h,
        "placements": placements,
        "offcuts": offcuts,
        "used_area": used,
        "efficiency": (used / board_area * 100.0) if board_area else 0.0,
    }


def optimize(pieces: list[dict[str, Any]], board_w: float, board_h: float,
             kerf: float = KERF_DEFAULT, margin: float = MARGIN_DEFAULT,
             allow_rotation: bool = True,
             descontar_cantos: bool = False,
             ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Acomoda las piezas en tantos tableros como haga falta.

    Args:
        descontar_cantos: si True, resta el espesor de canto de cada borde
            antes de añadir el kerf (flujo de taller con canteado propio).
            Si False, usa las cotas nominales del CSV (flujo proveedor).

    Returns:
        (sheets, unplaced)
        sheets: lista de dicts por tablero con sus 'placements' y eficiencia.
        unplaced: piezas que no caben ni en un tablero vacío.
    """
    usable_w, usable_h = _validar_tablero(board_w, board_h, margin)
    inflated = _inflar_piezas(pieces, kerf, descontar_cantos)
    boards, pending, frees = _mejor_empaquetado(
        usable_w, usable_h, inflated, allow_rotation)

    sheets: list[dict[str, Any]] = []
    for idx, placed in enumerate(boards):
        placements = _placements_tablero(placed, margin, kerf)
        offcuts = _retales_tablero(frees[idx], margin)
        sheets.append(_hoja_tablero(
            idx, board_w, board_h, placements, offcuts))

    unplaced: list[dict[str, Any]] = [{"name": p["name"], "w": p["w"] - kerf, "h": p["h"] - kerf,
                "material": p["material"]} for p in pending]
    return sheets, unplaced


MIN_OFFCUT = 80.0  # lado mínimo (mm) para considerar un sobrante reutilizable


def optimize_by_group(pieces: list[dict[str, Any]], board_w: float, board_h: float,
                      kerf: float = KERF_DEFAULT, margin: float = MARGIN_DEFAULT,
                      allow_rotation: bool = True,
                      descontar_cantos: bool = False) -> list[dict[str, Any]]:
    """Optimiza agrupando por (material, espesor).

    Args:
        descontar_cantos: se propaga a :func:`optimize`.

    Returns:
        lista de grupos:
        {"material", "thickness", "label", "sheets", "unplaced", "n_pieces"}
    """
    groups: dict[tuple[str, float], list[dict[str, Any]]] = {}
    for p in pieces:
        key = (p.get("material", "") or "", float(p.get("thickness", 0) or 0))
        groups.setdefault(key, []).append(p)

    result: list[dict[str, Any]] = []
    for (material, thickness), items in sorted(groups.items()):
        sheets, unplaced = optimize(items, board_w, board_h,
                                    kerf=kerf, margin=margin,
                                    allow_rotation=allow_rotation,
                                    descontar_cantos=descontar_cantos)
        result.append({
            "material": material,
            "thickness": thickness,
            "label": f"{material or 's/material'} · {thickness:g} mm",
            "sheets": sheets,
            "unplaced": unplaced,
            "n_pieces": len(items),
        })
    return result
