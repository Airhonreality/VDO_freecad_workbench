"""Operaciones de documento FreeCAD (escritura) que la UI necesita (D-31).

La UI no llama a ``recompute()`` ni a ``addObject()`` directamente: llama a
estas funciones. El comportamiento es el mismo que la llamada original.
"""

from __future__ import annotations

import FreeCAD as App


def recalcular(doc) -> None:
    """Recalcula el documento indicado."""
    doc.recompute()


def crear_grupo(doc, nombre: str):
    """Crea un grupo de objetos (App::DocumentObjectGroup) en el documento."""
    return doc.addObject("App::DocumentObjectGroup", nombre)


def recalcular_activo() -> None:
    """Recalcula el documento activo de FreeCAD."""
    App.ActiveDocument.recompute()
