"""app/casos_uso/crear_hoja.py — Caso de uso: crear hoja de melamina.

Crea un documento y asegura el entorno (hojas Params_Melamina y Params)
vía el Guardian de cad/. No escribe en objetos FreeCAD directamente.
"""

from __future__ import annotations

from freecad.vdo.core.dto import HojaDTO, HojaResultado
from freecad.vdo.cad.vdo_guardian import vdo_guard


def crear_hoja(doc, dto: HojaDTO) -> HojaResultado:
    """Asegura el entorno Guardián en el documento recibido."""
    if doc is None:
        raise ValueError("Documento requerido para crear la hoja.")
    vdo_guard(doc)
    return HojaResultado(nombre=doc.Name or dto.nombre)
