"""Decoradores de detección de entorno en tiempo de ejecución.

Cada decorador omite el test (SkipTest) solo si el entorno lo exige,
con el motivo exacto detectado. Nunca se usa una lista blanca de omisiones.
"""

from __future__ import annotations

import functools
import sys
import unittest


def _skip(motivo: str):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            raise unittest.SkipTest(motivo)
        return wrapper
    return deco


def requiere_freecad(fn=None, *, motivo: str | None = None):
    """Omite si no se puede importar FreeCAD de verdad (no mock)."""

    def _comprueba():
        try:
            import FreeCAD
            return True
        except ImportError:
            return False

    m = motivo or "requiere FreeCAD real (import FreeCAD falló)"
    if _comprueba():
        return (lambda f: f) if fn is None else fn
    return _skip(m)


def requiere_gui(fn=None, *, motivo: str | None = None):
    """Omite si no hay sesión gráfica (FreeCADGui + DISPLAY/WAYLAND_DISPLAY)."""

    def _comprueba():
        try:
            import FreeCADGui
        except ImportError:
            return False
        if not sys.stdout.isatty() and not (
            __import__("os").environ.get("DISPLAY")
            or __import__("os").environ.get("WAYLAND_DISPLAY")
        ):
            # No hay variable de display: entorno headless.
            return False
        return True

    m = motivo or "requiere GUI (FreeCADGui + DISPLAY/WAYLAND_DISPLAY)"
    if _comprueba():
        return (lambda f: f) if fn is None else fn
    return _skip(m)


def requiere_qt(fn=None, *, motivo: str | None = None):
    """Omite si PySide6 no es importable."""

    def _comprueba():
        try:
            import PySide6
            return True
        except ImportError:
            return False

    m = motivo or "requiere PySide6 (import falló)"
    if _comprueba():
        return (lambda f: f) if fn is None else fn
    return _skip(m)


__all__ = ["requiere_freecad", "requiere_gui", "requiere_qt"]
