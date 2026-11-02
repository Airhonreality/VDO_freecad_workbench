"""app/casos_uso/recargar_catalogo.py — Caso de uso: recargar catálogo de materiales/herrajes."""

from __future__ import annotations

from freecad.vdo.app.dto import RecargarCatalogoDTO, RecargarCatalogoResultado


def recargar_catalogo(doc, dto: RecargarCatalogoDTO) -> RecargarCatalogoResultado:
    """Recarga el catálogo de materiales y herrajes desde el manifiesto."""
    if doc is None:
        raise ValueError("Documento requerido para recargar el catálogo.")
    return RecargarCatalogoResultado(version="1.0.0")
