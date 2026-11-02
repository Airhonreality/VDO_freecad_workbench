"""app/casos_uso/consultar_herrajes.py — Caso de uso: consultar catálogo de herrajes."""

from __future__ import annotations

from freecad.vdo.app.dto import ConsultarHerrajesDTO, ConsultarHerrajesResultado


def consultar_herrajes(doc, dto: ConsultarHerrajesDTO) -> ConsultarHerrajesResultado:
    """Consulta herrajes disponibles por tipo."""
    if doc is None:
        raise ValueError("Documento requerido para consultar herrajes.")
    herrajes = []
    if dto.tipo is None or dto.tipo == "tirador":
        herrajes.append({"tipo": "tirador", "sku": "TIR-001"})
    if dto.tipo is None or dto.tipo == "bisagra":
        herrajes.append({"tipo": "bisagra", "sku": "BIS-001"})
    if dto.tipo is None or dto.tipo == "guia":
        herrajes.append({"tipo": "guia", "sku": "GUI-001"})
    return ConsultarHerrajesResultado(herrajes=herrajes)
