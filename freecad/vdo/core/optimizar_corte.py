"""core/optimizar_corte.py — Caso de uso: optimizador de corte."""

from __future__ import annotations

from freecad.vdo.core.dto import OptimizarCorteDTO, OptimizarCorteResultado


def optimizar_corte(doc, dto: OptimizarCorteDTO) -> OptimizarCorteResultado:
    """Optimiza el corte de tableros para una lista de módulos."""
    if doc is None:
        raise ValueError("Documento requerido para optimizar el corte.")
    total_area = dto.ancho_tablero * dto.alto_tablero
    if total_area <= 0:
        return OptimizarCorteResultado(eficiencia=0.0, desperdicio=1.0)
    area_usada = sum(
        (m.get("ancho", 0) * m.get("alto", 0)) for m in dto.modulos
    )
    eficiencia = min(area_usada / total_area, 1.0)
    return OptimizarCorteResultado(eficiencia=eficiencia, desperdicio=1.0 - eficiencia)
