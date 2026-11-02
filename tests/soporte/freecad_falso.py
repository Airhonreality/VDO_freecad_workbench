# -*- coding: utf-8 -*-
"""Contexto para instalar y restaurar mocks de FreeCAD/Part en sys.modules.

Uso:

    from tests.soporte.freecad_falso import instalado

    class MiTest(unittest.TestCase):
        def setUp(self):
            self._ctx = instalado()
            self._ctx.__enter__()

        def tearDown(self):
            self._ctx.__exit__(None, None, None)

O como decorador:

    @instalado()
    def test_algo(self):
        ...

El contexto coloca `FreeCAD`, `Part` (y alias) en ``sys.modules`` al entrar y
los **restaura** al salir (o los elimina si no existían antes), evitando
contaminación entre tests y entre procesos.
"""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Optional


class _MockVector:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z


class _MockPart:
    class Face:
        def __init__(self, wire):
            self.wire = wire

        def extrude(self, vector):
            m = _MockShape()
            m.Volume = 100.0
            m.isValid.return_value = True
            m.cut.return_value = m
            return m

    @staticmethod
    def makeBox(x, y, z, base=None):
        m = _MockShape()
        m.Volume = float(x) * float(y) * float(z)
        m.isValid.return_value = True
        m.cut.return_value = m
        return m

    @staticmethod
    def makeCylinder(radius, height, base=None, direction=None):
        m = _MockShape()
        m.Volume = 3.14159 * float(radius) ** 2 * float(height)
        m.isValid.return_value = True
        m.cut.return_value = m
        return m

    @staticmethod
    def makePolygon(points, closed=False):
        m = _MockShape()
        m.isValid.return_value = True
        return m

    @staticmethod
    def makeCompound(solids):
        m = _MockShape()
        m.Volume = sum(getattr(s, "Volume", 0) for s in solids)
        m.isValid.return_value = True
        return m


class _MockShape:
    Volume = 0.0

    def isValid(self):
        return True

    def cut(self, tool):
        m = _MockShape()
        m.Volume = self.Volume
        return m


class _MockConsole:
    @staticmethod
    def PrintError(msg):
        pass

    @staticmethod
    def PrintWarning(msg):
        pass

    @staticmethod
    def PrintMessage(msg):
        pass


class _MockApp:
    Console = _MockConsole()
    GuiUp = False

    @staticmethod
    def getUserMacroDir(create=False):
        return "/tmp/freecad_macro"

    newDocument = staticmethod(lambda nombre: None)
    ActiveDocument = None

    @staticmethod
    def closeDocument(nombre):
        pass


class instalado:
    """Context manager que instala mocks de FreeCAD/Part en sys.modules.

    Params
    ------
    usar_mock : bool
        Si False (y hay FreeCAD real), no sustituye nada.
    """

    _MODULOS = ("FreeCAD", "Part")

    def __init__(self, usar_mock: Optional[bool] = None):
        if usar_mock is None:
            try:
                import FreeCAD  # noqa: F401
                usar_mock = False
            except ImportError:
                usar_mock = True
        self.usar_mock = usar_mock
        self._previos: dict[str, Optional[ModuleType]] = {}

    def __enter__(self):
        if not self.usar_mock:
            return self
        for nombre in self._MODULOS:
            self._previos[nombre] = sys.modules.get(nombre)
        if "FreeCAD" not in sys.modules:
            mock_app = _MockApp()
            mock_app.App = mock_app
            mock_app.Vector = _MockVector
            sys.modules["FreeCAD"] = mock_app
        if "Part" not in sys.modules:
            sys.modules["Part"] = _MockPart()
        return self

    def __exit__(self, exc_tipo, exc_val, exc_tb):
        if not self.usar_mock:
            return False
        for nombre in self._MODULOS:
            previo = self._previos.get(nombre)
            if previo is None:
                sys.modules.pop(nombre, None)
            else:
                sys.modules[nombre] = previo
        self._previos.clear()
        return False


def requiere_freecad(mensaje="requiere FreeCAD real"):
    """Decorador de clase/método que salta si no hay FreeCAD real.

    Verifica que FreeCAD sea un módulo genuino (no un mock instalado por
    ``instalado()`` en ``sys.modules``) y que tenga ``newDocument``.
    """
    try:
        import FreeCAD
        desde_mock = not isinstance(FreeCAD, ModuleType)
        disponible = (not desde_mock) and hasattr(FreeCAD, "newDocument")
    except ImportError:
        disponible = False

    import unittest

    return unittest.skipUnless(disponible, mensaje)


def requiere_qt(mensaje="requiere Qt / PySide"):
    """Decorador de clase/método que salta si no hay PySide."""
    try:
        from PySide6 import QtCore  # noqa: F401
        disponible = True
    except ImportError:
        try:
            from PySide2 import QtCore  # noqa: F401
            disponible = True
        except ImportError:
            disponible = False

    import unittest

    return unittest.skipUnless(disponible, mensaje)
