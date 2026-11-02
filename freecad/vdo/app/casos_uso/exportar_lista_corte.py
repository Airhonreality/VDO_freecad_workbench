"""app/casos_uso/exportar_lista_corte.py — Caso de uso: exportar lista de corte."""

from __future__ import annotations

from freecad.vdo.app.dto import ExportarListaCorteDTO, ExportarListaCorteResultado


def exportar_lista_corte(doc, dto: ExportarListaCorteDTO) -> ExportarListaCorteResultado:
    """Exporta la lista de corte de un módulo."""
    if doc is None:
        raise ValueError("Documento requerido para exportar la lista de corte.")
    obj = doc.getObject(dto.modulo)
    if obj is None:
        return ExportarListaCorteResultado(archivo="", piezas=0)
    # Delegar a cad/ para la escritura real (pendiente de mover a cad/)
    return ExportarListaCorteResultado(archivo=f"{dto.modulo}.{dto.formato}", piezas=0)
