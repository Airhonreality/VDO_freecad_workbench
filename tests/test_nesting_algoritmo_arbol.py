"""Snapshot del árbol de widgets del grupo Algoritmo de NestingDialog (F-UI-2).

Capturado antes de migrar ``_construir_algoritmo`` a FormBuilder. Compara el
árbol completo (clases, textos, valores, rangos, tooltips, visibilidad y orden)
con ``tests/fixtures/nesting_algoritmo_snapshot.json``.
"""

import importlib
import json
import os
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

from tests.soporte.arbol_widgets import volcar_arbol
from tests.soporte.qt import qapplication
from tests.soporte.requisitos import requiere_freecad, requiere_qt

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from freecad.vdo import qt_compat
from freecad.vdo.cad import documento
from freecad.vdo.core import nesting_presets as NP
from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui import qt

RAIZ = Path(__file__).resolve().parent.parent
SNAPSHOT = RAIZ / "tests" / "fixtures" / "nesting_algoritmo_snapshot.json"


class _Grupo:
    """ParamGet en memoria para no tocar las preferencias del usuario."""

    def __init__(self, valores=None):
        self.valores = dict(valores or {})

    def GetString(self, clave, defecto=""):
        return self.valores.get(clave, defecto)

    def SetString(self, clave, valor):
        self.valores[clave] = valor


def _stubs_addon_nesting() -> dict:
    nombres = ["freecad.nestingworkbench", "freecad.nestingworkbench.Tools",
               "freecad.nestingworkbench.Tools.Nesting",
               "freecad.nestingworkbench.Tools.Nesting.nesting_logic",
               "freecad.nestingworkbench.Tools.Nesting.shape_preparer", "FreeCADGui"]
    stubs = {n: types.ModuleType(n) for n in nombres}
    stubs["freecad.nestingworkbench.Tools.Nesting.nesting_logic"].nest = None
    stubs["freecad.nestingworkbench.Tools.Nesting.shape_preparer"].ShapePreparer = None
    return stubs


@requiere_freecad
@requiere_qt
class NestingAlgoritmoArbolTests(unittest.TestCase):

    def setUp(self):
        qapplication()
        parche_sys = mock.patch.dict(sys.modules, _stubs_addon_nesting())
        parche_sys.start()
        self.addCleanup(parche_sys.stop)
        self.wf = importlib.import_module("freecad.vdo.ui.nesting_workflow")

    def _abrir(self):
        parche = mock.patch.object(NP.NestingPresetManager, "get_prefs",
                                   return_value=_Grupo())
        parche.start()
        self.addCleanup(parche.stop)
        dlg = self.wf.NestingDialog()
        self.addCleanup(dlg.deleteLater)
        return dlg

    def _grupo_algoritmo(self, dlg):
        for grupo in dlg.findChildren(QtWidgets.QGroupBox):
            if "Algoritmo de Optimización" in grupo.title():
                return grupo
        self.fail("no se encontró el grupo Algoritmo de Optimización")

    def test_arbol_identico_al_snapshot(self):
        grupo = self._grupo_algoritmo(self._abrir())
        esperado = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        self.assertEqual(volcar_arbol(grupo), esperado)

    def test_el_volcado_detecta_un_cambio(self):
        grupo = self._grupo_algoritmo(self._abrir())
        esperado = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        etiquetas = grupo.findChildren(QtWidgets.QLabel)
        self.assertTrue(etiquetas)
        etiquetas[0].setText("cambio")
        self.assertNotEqual(volcar_arbol(grupo), esperado)


if __name__ == "__main__":
    unittest.main()
