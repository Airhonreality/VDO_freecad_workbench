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
def _area(r):
    return r[2] * r[3]


def _intersects(a, b):
    return not (b[0] >= a[0] + a[2] or b[0] + b[2] <= a[0] or
                b[1] >= a[1] + a[3] or b[1] + b[3] <= a[1])


def _contains(outer, inner):
    return (inner[0] >= outer[0] and inner[1] >= outer[1] and
            inner[0] + inner[2] <= outer[0] + outer[2] + 1e-9 and
            inner[1] + inner[3] <= outer[1] + outer[3] + 1e-9)


def _prune(rects):
    """Elimina rectángulos libres contenidos en otro (MaxRects prune)."""
    rects = [r for r in rects if r[2] > 1e-6 and r[3] > 1e-6]
    keep = []
    for i, r in enumerate(rects):
        contained = False
        for j, s in enumerate(rects):
            if i == j:
                continue
            if _contains(s, r):
                # Si son idénticos, conservar solo el de menor índice.
                if _area(s) > _area(r) or (abs(_area(s) - _area(r)) < 1e-9 and j < i):
                    contained = True
                    break
        if not contained:
            keep.append(r)
    return keep


def _split_free(free, used):
    """Divide los rectángulos libres alrededor de la pieza colocada."""
    new = []
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


def _pack_bin(bin_w, bin_h, items, allow_rotation, score_func):
    """Empaqueta lo que quepa en un tablero. Devuelve (placed, remaining)."""
    free = [[0.0, 0.0, float(bin_w), float(bin_h)]]
    placed = []
    remaining = []

    for it in items:
        best = None  # (score, x, y, w, h, rotated)
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


def _pack_all(usable_w, usable_h, items, allow_rotation, score_func):
    """Empaqueta en tantos tableros como haga falta con una estrategia.

    Devuelve (lista_de_tableros, pendientes). Cada tablero es una lista de
    placements crudos {"item", "x", "y", "w", "h", "rotated"}.
    """
    boards = []
    frees = []
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
def _validar_tablero(board_w, board_h, margin):
    """Devuelve las dimensiones utiles del tablero; rechaza margen excesivo."""
    usable_w = board_w - 2 * margin
    usable_h = board_h - 2 * margin
    if usable_w <= 0 or usable_h <= 0:
        raise ValueError("El margen es mayor que el tablero.")
    return usable_w, usable_h


def _inflar_piezas(pieces, kerf, descontar_cantos):
    """Infla cada pieza por el kerf: garantiza separacion de corte."""
    inflated = []
    for p in pieces:
        w, h = _medidas_corte(p, descontar_cantos)
        inflated.append({"name": p["name"], "material": p["material"],
                         "thickness": p.get("thickness"),
                         "w": w + kerf, "h": h + kerf})
    return inflated


def _mejor_empaquetado(usable_w, usable_h, inflated, allow_rotation):
    """Prueba heuristica x orden y devuelve (boards, pending, frees) del mejor."""
    best = None
    for _hname, score_func in _HEURISTICS.items():
        for _sname, skey in _SORTERS.items():
            ordered = sorted(inflated, key=skey, reverse=True)
            boards, pending, frees = _pack_all(usable_w, usable_h, ordered,
                                               allow_rotation, score_func)
            placed_area = sum(pl["w"] * pl["h"] for b in boards for pl in b)
            key = (len(boards) if boards else 10 ** 9, -placed_area)
            if best is None or key < best[0]:
                best = (key, boards, pending, frees)
    return best[1], best[2], best[3]


def _placements_tablero(placed, margin, kerf):
    """Piezas colocadas en un tablero, con coordenadas reales del tablero."""
    placements = []
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


def _retales_tablero(frees, margin):
    """Rectangulos libres del tablero (sobrante reutilizable) en mm reales."""
    offcuts = []
    for fr in frees:
        if fr[2] > 1e-6 and fr[3] > 1e-6:
            offcuts.append({
                "x": fr[0] + margin,
                "y": fr[1] + margin,
                "w": fr[2],
                "h": fr[3],
            })
    return offcuts


def _hoja_tablero(idx, board_w, board_h, placements, offcuts):
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


def optimize(pieces, board_w, board_h,
             kerf=KERF_DEFAULT, margin=MARGIN_DEFAULT,
             allow_rotation=True, descontar_cantos=False):
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

    sheets = []
    for idx, placed in enumerate(boards):
        placements = _placements_tablero(placed, margin, kerf)
        offcuts = _retales_tablero(frees[idx], margin)
        sheets.append(_hoja_tablero(
            idx, board_w, board_h, placements, offcuts))

    unplaced = [{"name": p["name"], "w": p["w"] - kerf, "h": p["h"] - kerf,
                "material": p["material"]} for p in pending]
    return sheets, unplaced


MIN_OFFCUT = 80.0  # lado mínimo (mm) para considerar un sobrante reutilizable


def optimize_by_group(pieces, board_w, board_h,
                      kerf=KERF_DEFAULT, margin=MARGIN_DEFAULT,
                      allow_rotation=True, descontar_cantos=False):
    """Optimiza agrupando por (material, espesor).

    Args:
        descontar_cantos: se propaga a :func:`optimize`.

    Returns:
        lista de grupos:
        {"material", "thickness", "label", "sheets", "unplaced", "n_pieces"}
    """
    groups = {}
    for p in pieces:
        key = (p.get("material", "") or "", float(p.get("thickness", 0) or 0))
        groups.setdefault(key, []).append(p)

    result = []
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


def _retal_area(sheet, min_side=MIN_OFFCUT):
    return sum(o["w"] * o["h"] for o in sheet.get("offcuts", [])
               if min(o["w"], o["h"]) >= min_side)


def resumen_global(groups, board_w, board_h):
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


def resumen(sheets, unplaced):
    """Devuelve un texto-resumen legible del resultado."""
    lines = []
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
