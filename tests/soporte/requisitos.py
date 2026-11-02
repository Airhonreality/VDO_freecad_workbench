"""Decoradores de detección de entorno en tiempo de ejecución.

Un test se omite (``unittest.SkipTest`` con motivo) solo si el entorno lo
exige. Nunca por lista. Sirven para funciones y para clases.

Detección:
  - ``requiere_freecad``: el ``FreeCAD`` importado debe ser el binario real.
    Un mock de ``freecad_falso`` en ``sys.modules`` NO cuenta: el binario real
    expone ``Version()`` y ``getHomePath()``, y el mock no las define.
  - ``requiere_gui``: FreeCAD real con ``GuiUp`` activo, ``FreeCADGui``
    importable y ``DISPLAY`` o ``WAYLAND_DISPLAY`` definidos.
  - ``requiere_qt``: alguno de PySide6, PySide2 o PySide importable.

Uso:
    @requiere_freecad
    class MiTests(unittest.TestCase): ...

    @requiere_gui(motivo="necesita panel")
    def test_panel(self): ...
"""

from __future__ import annotations

import importlib
import os
import unittest
from collections.abc import Callable
from typing import Any


def _freecad_real() -> Any | None:
    """Devuelve el módulo FreeCAD real o None. Un mock no supera la comprobación."""
    try:
        fc = importlib.import_module("FreeCAD")
    except ImportError:
        return None
    version = getattr(fc, "Version", None)
    home = getattr(fc, "getHomePath", None)
    if not callable(version) or not callable(home):
        return None
    try:
        v = version()
        h = home()
    except (TypeError, AttributeError, RuntimeError):
        return None
    if not isinstance(v, list) or not v or not h:
        return None
    return fc


def _gui_real() -> bool:
    fc = _freecad_real()
    if fc is None or not getattr(fc, "GuiUp", 0):
        return False
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return False
    try:
        importlib.import_module("FreeCADGui")
    except ImportError:
        return False
    return True


def _qt_disponible() -> bool:
    for nombre in ("PySide6", "PySide2", "PySide"):
        try:
            importlib.import_module(nombre)
        except ImportError:
            continue
        return True
    return False


def _fabrica(condicion: Callable[[], bool], motivo_defecto: str):
    """Crea un decorador con y sin argumentos. Omite solo si ``condicion()`` es falsa."""

    def decorador_con_motivo(fn=None, *, motivo: str | None = None):
        texto = motivo or motivo_defecto

        def aplicar(obj):
            if condicion():
                return obj
            return unittest.skip(texto)(obj)

        return aplicar if fn is None else aplicar(fn)

    return decorador_con_motivo


requiere_freecad = _fabrica(
    lambda: _freecad_real() is not None,
    "requiere FreeCAD real (import falló o solo hay un mock)",
)
requiere_gui = _fabrica(
    _gui_real,
    "requiere FreeCAD con GUI (GuiUp, FreeCADGui y DISPLAY/WAYLAND_DISPLAY)",
)
requiere_qt = _fabrica(
    _qt_disponible,
    "requiere PySide6/PySide2/PySide (ninguno importable)",
)

__all__ = ["requiere_freecad", "requiere_gui", "requiere_qt"]
