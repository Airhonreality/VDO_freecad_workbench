"""Snapshot del árbol de widgets del panel de medidas de VDOBoxControllerWidget (F-UI-2b).

Capturado antes de migrar ``_construir_panel_medidas`` a FormBuilder. Compara el
árbol completo (clases, textos, valores, rangos, tooltips, visibilidad y orden)
con ``tests/fixtures/box_panel_medidas_snapshot.json``.
"""

import json
import os
import unittest
from pathlib import Path

from tests.soporte.arbol_widgets import volcar_arbol
from tests.soporte.qt import qapplication
from tests.soporte.requisitos import requiere_freecad, requiere_qt

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui.box_controller import VDOBoxControllerWidget

RAIZ = Path(__file__).resolve().parent.parent
SNAPSHOT = RAIZ / "tests" / "fixtures" / "box_panel_medidas_snapshot.json"


@requiere_freecad
@requiere_qt
class BoxPanelMedidasArbolTests(unittest.TestCase):

    def setUp(self):
        qapplication()

    def _widget(self):
        widget = VDOBoxControllerWidget()
        self.addCleanup(widget.deleteLater)
        return widget

    def test_arbol_identico_al_snapshot(self):
        panel = self._widget().panel_medidas
        esperado = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        self.assertEqual(volcar_arbol(panel), esperado)

    def test_el_volcado_detecta_un_cambio(self):
        panel = self._widget().panel_medidas
        esperado = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        etiquetas = panel.findChildren(QtWidgets.QLabel)
        self.assertTrue(etiquetas)
        etiquetas[0].setText("cambio")
        self.assertNotEqual(volcar_arbol(panel), esperado)


if __name__ == "__main__":
    unittest.main()
