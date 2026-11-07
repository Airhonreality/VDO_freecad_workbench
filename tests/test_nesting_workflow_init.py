"""D-100: el workflow de Nesting inicializa los presets por defecto al abrirse.

Antes, la inicializacion ocurria al importar core/nesting_presets. Ahora la llama
NestingDialog al construirse, una vez por sesion. Las preferencias son un ParamGet
en memoria (no se tocan las del usuario). El addon Nesting Workbench no esta
instalado en el entorno de pruebas: se sustituye por stubs solo durante el import.
"""

import importlib
import json
import os
import sys
import types
import unittest
from unittest import mock

from tests.soporte.qt import qapplication
from tests.soporte.requisitos import requiere_freecad, requiere_qt

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Modulos del paquete que se importan ANTES de parchear sys.modules, para que
# patch.dict no los retire al terminar (solo se retira nesting_workflow).
from freecad.vdo import qt_compat
from freecad.vdo.cad import documento
from freecad.vdo.core import nesting_presets as NP
from freecad.vdo.ui import qt, tema


class _Grupo:
    """ParamGet en memoria que cuenta las escrituras."""

    def __init__(self, valores=None):
        self.valores = dict(valores or {})
        self.escrituras = 0

    def GetString(self, clave, defecto=""):
        return self.valores.get(clave, defecto)

    def SetString(self, clave, valor):
        self.escrituras += 1
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
class NestingWorkflowInicializaPresetsTests(unittest.TestCase):

    def setUp(self):
        qapplication()
        parche_sys = mock.patch.dict(sys.modules, _stubs_addon_nesting())
        parche_sys.start()
        self.addCleanup(parche_sys.stop)
        # import_module consulta sys.modules: el modulo se reimporta en cada prueba
        # (la bandera de una sola vez vuelve a False). 'from paquete import modulo' no.
        self.wf = importlib.import_module("freecad.vdo.ui.nesting_workflow")

    def _abrir(self, grupo):
        parche = mock.patch.object(NP.NestingPresetManager, "get_prefs",
                                   return_value=grupo)
        parche.start()
        self.addCleanup(parche.stop)
        dlg = self.wf.NestingDialog()
        self.addCleanup(dlg.deleteLater)
        return dlg

    def test_abrir_workflow_inicializa_presets_por_defecto(self):
        grupo = _Grupo()
        self._abrir(grupo)
        guardado = json.loads(grupo.valores["Presets"])
        self.assertEqual(guardado["presets"], json.loads(json.dumps(NP.DEFAULT_PRESETS)))
        self.assertEqual(guardado["list"], list(NP.DEFAULT_PRESETS.keys()))

    def test_no_reescribe_preferencia_existente(self):
        existente = json.dumps({"list": ["Propio"], "presets": {"Propio": {"width": 1}}})
        grupo = _Grupo({"Presets": existente})
        self._abrir(grupo)
        self.assertEqual(grupo.valores["Presets"], existente)
        self.assertEqual(grupo.escrituras, 0)

    def test_inicializa_una_sola_vez_por_sesion(self):
        grupo = _Grupo()
        parche = mock.patch.object(NP.NestingPresetManager, "get_prefs",
                                   return_value=grupo)
        parche.start()
        self.addCleanup(parche.stop)
        for _ in range(2):
            dlg = self.wf.NestingDialog()
            self.addCleanup(dlg.deleteLater)
        self.assertEqual(grupo.escrituras, 1)


if __name__ == "__main__":
    unittest.main()
