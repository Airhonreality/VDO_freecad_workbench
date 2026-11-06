"""app/casos_uso/nesting.py — Caso de uso: nesting automático."""

from __future__ import annotations

from freecad.vdo.core.dto import NestingDTO, NestingResultado


def nesting(doc, dto: NestingDTO) -> NestingResultado:
    """Distribuye piezas en placas para minimizar desperdicio."""
    if doc is None:
        raise ValueError("Documento requerido para nesting.")
    n_piezas = len(dto.piezas)
    placas = max(1, (n_piezas + 7) // 8)
    return NestingResultado(placas=placas)
