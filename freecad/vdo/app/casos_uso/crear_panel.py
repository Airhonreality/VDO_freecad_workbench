"""app/casos_uso/crear_panel.py — Caso de uso: crear panel L1.

Orquesta: recibe doc (puerto) y un PanelDTO, llama a crear_pieza de core/
pasándole el documento, y devuelve un PanelResultado.
"""

from __future__ import annotations

from freecad.vdo.core.dto import PanelDTO, PanelResultado
from freecad.vdo.core.vdo_panel_core import crear_pieza


def crear_panel(doc, dto: PanelDTO) -> PanelResultado:
    """Crea un panel en el documento usando el plano puro de core/."""
    if doc is None:
        raise ValueError("Documento requerido para crear el panel.")
    cfg = {
        "nombre": dto.nombre,
        "etiqueta": dto.etiqueta,
        "orientacion": dto.orientacion,
        "largo": dto.largo,
        "ancho": dto.ancho,
        "espesor": dto.espesor,
        "cantos": dto.cantos,
        "material_ref": dto.material_ref,
        "usar_params": dto.usar_params,
        "rotacion": dto.rotacion,
        "anclaje": dto.anclaje,
    }
    obj = crear_pieza(doc, cfg)
    if obj is None:
        return PanelResultado(nombre=dto.nombre, volumen=0.0)
    return PanelResultado(nombre=obj.Name, volumen=float(obj.Shape.Volume))
