"""Utilidades compartidas para eliminar código duplicado entre módulos de core.

Proporciona importadores perezosos de FreeCAD y Part para que cada módulo de
core no tenga que definir sus propias copias de ``_get_app`` y ``_get_part``.
"""

from __future__ import annotations

from typing import Any

# Eje local -> campo de dimensión de la caja (x = largo "w", y = ancho "h", z = espesor "d").
# Lo usan core/vdo_reengrose y cad/geometria: una sola definición (M2, H-06).
DIMENSION_POR_EJE = {"x": "w", "y": "h", "z": "d"}


def _get_app() -> Any:  # FreeCAD no tiene tipos: el módulo importado es Any
    """Importa FreeCAD de forma perezosa."""
    import FreeCAD as App
    return App


def _get_part() -> Any:  # Part no tiene tipos: el módulo importado es Any
    """Importa Part de forma perezosa."""
    import Part
    return Part


