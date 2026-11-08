"""Snapshot del árbol de widgets de la subdivisión de vano (F-UI-2).

Capturado antes de migrar ``PaginaVano._crear_panel_subdivision`` a FormBuilder.
Compara el árbol completo (clases, textos, valores, rangos, tooltips, visibilidad
y orden) con ``tests/fixtures/inspector_pagina_vano_subdivision_snapshot.json``.

``PaginaVano`` se instancia directamente (no necesita diálogo).
"""

import importlib
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

from tests.soporte.arbol_widgets import volcar_arbol
from tests.soporte.qt import qapplication
from tests.soporte.requisitos import requiere_freecad, requiere_qt

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from freecad.vdo.qt_compat import QtWidgets

RAIZ = Path(__file__).resolve().parent.parent
SNAPSHOT = RAIZ / "tests" / "fixtures" / "inspector_pagina_vano_subdivision_snapshot.json"


def _stubs_addon_nesting() -> dict:
    """Stubs del addon nesting por si la cadena de import de inspector_pagina_vano
    lo requiere (modelado en tests/test_nesting_workflow_init.py)."""
    nombres = ["freecad.nestingworkbench", "freecad.nestingworkbench.Tools",
               "freecad.nestingworkbench.Tools.Nesting",
               "freecad.nestingworkbench.Tools.Nesting.nesting_logic",
               "freecad.nestingworkbench.Tools.Nesting.shape_preparer", "FreeCADGui"]
    stubs = {n: __import__("types").ModuleType(n) for n in nombres}
    stubs["freecad.nestingworkbench.Tools.Nesting.nesting_logic"].nest = None
    stubs["freecad.nestingworkbench.Tools.Nesting.shape_preparer"].ShapePreparer = None
    return stubs


def _panel_subdivision(pagina):
    """Localiza el panel de subdivisión: el QWidget que contiene un QLabel
    con texto exactamente ``"Eje:"`` como hijo directo."""
    for etiqueta in pagina.findChildren(QtWidgets.QLabel):
        if etiqueta.text() == "Eje:":
            return etiqueta.parentWidget()
    raise AssertionError("no se encontró el panel de subdivisión (QLabel 'Eje:')")


@requiere_freecad
@requiere_qt
class InspectorPaginaVanoSubdivisionArbolTests(unittest.TestCase):

    def setUp(self):
        qapplication()
        parche_sys = mock.patch.dict(sys.modules, _stubs_addon_nesting())
        parche_sys.start()
        self.addCleanup(parche_sys.stop)
        self.pagina = importlib.import_module(
            "freecad.vdo.ui.inspector_pagina_vano").PaginaVano()
        self.addCleanup(self.pagina.deleteLater)

    def test_arbol_identico_al_snapshot(self):
        panel = _panel_subdivision(self.pagina)
        esperado = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        self.assertEqual(volcar_arbol(panel), esperado)

    def test_el_volcado_detecta_un_cambio(self):
        panel = _panel_subdivision(self.pagina)
        esperado = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        etiquetas = panel.findChildren(QtWidgets.QLabel)
        self.assertTrue(etiquetas)
        etiquetas[0].setText("cambio")
        self.assertNotEqual(volcar_arbol(panel), esperado)


if __name__ == "__main__":
    unittest.main()
