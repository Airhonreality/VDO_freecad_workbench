#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI del optimizador de corte 2D (herramienta de desarrollo, fuera del paquete).

Uso: python3 tools/vdo_optimizador_cli.py --csv lista.csv [--board 2440x1830] [--out plan.svg]

Vive en tools/ porque genera un SVG con la capa de interfaz (ui/): el motor no debe
depender de la UI (D24).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from freecad.vdo.core.vdo_optimizer_core import (  # noqa: E402
    KERF_DEFAULT, MARGIN_DEFAULT, expand_pieces, optimize_by_group,
    read_cutting_csv, resumen_global)


# ----------------------------------------------------------------------
# 4. CLI
# ----------------------------------------------------------------------
def _parse_board(text):
    try:
        w, h = text.lower().split("x")
        return float(w), float(h)
    except (ValueError, AttributeError):
        raise argparse.ArgumentTypeError("Formato de tablero: ANCHOxALTO (ej: 2440x1830)")


def main():
    ap = argparse.ArgumentParser(
        description="VDO Optimizador de corte 2D (nesting de rectángulos)")
    ap.add_argument("--csv", required=True, help="Lista de corte CSV")
    ap.add_argument("--board", type=_parse_board, default=(2440.0, 1830.0),
                    help="Tablero ANCHOxALTO en mm (default 2440x1830)")
    ap.add_argument("--kerf", type=float, default=KERF_DEFAULT,
                    help="Grosor de sierra mm (default 4)")
    ap.add_argument("--margin", type=float, default=MARGIN_DEFAULT,
                    help="Margen perimetral mm (default 10)")
    ap.add_argument("--no-rotate", action="store_true",
                    help="No rotar piezas (respetar veta)")
    ap.add_argument("--descontar-cantos", action="store_true",
                    help="Descontar el espesor de canto de las cotas "
                         "nominales antes del kerf (canteado propio)")
    ap.add_argument("--out", default="vdo_cut_plan.svg",
                    help="Ruta del SVG de salida")
    args = ap.parse_args()

    parts = read_cutting_csv(args.csv)
    if not parts:
        print("❌ No se encontraron piezas en el CSV")
        return 1

    board_w, board_h = args.board
    groups = optimize_by_group(
        expand_pieces(parts), board_w, board_h,
        kerf=args.kerf, margin=args.margin,
        allow_rotation=not args.no_rotate,
        descontar_cantos=args.descontar_cantos)

    sheets = [s for g in groups for s in g["sheets"]]
    unplaced = [u for g in groups for u in g["unplaced"]]

    from freecad.vdo.ui import vdo_optimizer_preview as preview  # capa de interfaz
    preview.render_svg(sheets, unplaced, args.out,
                       board_w=board_w, board_h=board_h,
                       kerf=args.kerf, margin=args.margin)

    tot = resumen_global(groups, board_w, board_h)
    print("=" * 60)
    print("VDO OPTIMIZADOR DE CORTE")
    print("=" * 60)
    for g in groups:
        print(f"  {g['label']}: {len(g['sheets'])} tablero(s), "
              f"{g['n_pieces'] - len(g['unplaced'])}/{g['n_pieces']} piezas")
    print(f"\nPiezas: {tot['n_placed']}/{tot['n_total']} · "
          f"Tableros: {tot['n_boards']} · "
          f"Aprovechamiento: {tot['efficiency']:.1f}% · "
          f"Retal: {tot['retal_m2']:.2f} m²")
    if tot["n_unplaced"]:
        print(f"⚠️  No colocadas: {tot['n_unplaced']}")
    print(f"\n📐 Preview SVG: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
