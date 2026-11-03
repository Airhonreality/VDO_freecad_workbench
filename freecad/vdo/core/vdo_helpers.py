"""Utilidades compartidas para eliminar código duplicado entre módulos de core.

Proporciona importadores perezosos de FreeCAD y Part para que cada módulo de
core no tenga que definir sus propias copias de ``_get_app`` y ``_get_part``.
"""

from __future__ import annotations


def _get_app():
    """Importa FreeCAD de forma perezosa."""
    import FreeCAD as App
    return App


def _get_part():
    """Importa Part de forma perezosa."""
    import Part
    return Part


def rotacion_z(grados):
    """Rotación alrededor de Z; el ángulo entra en grados."""
    app = _get_app()
    return app.Rotation(app.Vector(0.0, 0.0, 1.0), float(grados))
