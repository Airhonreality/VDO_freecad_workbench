"""Operaciones de documento FreeCAD (escritura) que la UI necesita (D-31).

La UI no llama a ``recompute()`` ni a ``addObject()`` directamente: llama a
estas funciones. El comportamiento es el mismo que la llamada original.
"""

from __future__ import annotations

import FreeCAD as App


def recalcular(doc) -> None:
    """Recalcula el documento indicado."""
    doc.recompute()


def crear_objeto(doc, tipo: str, nombre: str):
    """Crea un objeto de FreeCAD de tipo ``tipo`` en el documento."""
    return doc.addObject(tipo, nombre)


def eliminar_objeto(doc, nombre: str) -> None:
    """Elimina del documento el objeto de nombre ``nombre``."""
    doc.removeObject(nombre)


def crear_grupo(doc, nombre: str):
    """Crea un grupo de objetos (App::DocumentObjectGroup) en el documento."""
    return doc.addObject("App::DocumentObjectGroup", nombre)


def recalcular_activo() -> None:
    """Recalcula el documento activo de FreeCAD."""
    App.ActiveDocument.recompute()
