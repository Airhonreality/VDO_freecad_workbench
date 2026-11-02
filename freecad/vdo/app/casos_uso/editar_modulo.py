"""app/casos_uso/editar_modulo.py — Caso de uso: editar módulo existente."""

from __future__ import annotations

from freecad.vdo.app.dto import EditarModuloDTO, EditarModuloResultado


def editar_modulo(doc, dto: EditarModuloDTO) -> EditarModuloResultado:
    """Edita un módulo existente en el documento."""
    if doc is None:
        raise ValueError("Documento requerido para editar el módulo.")
    obj = doc.getObject(dto.nombre)
    if obj is None:
        return EditarModuloResultado(nombre=dto.nombre, aplicado=False)
    aplicado = False
    for clave, valor in dto.cambios.items():
        if hasattr(obj, clave):
            setattr(obj, clave, valor)
            aplicado = True
    doc.recompute()
    return EditarModuloResultado(nombre=dto.nombre, aplicado=aplicado)
