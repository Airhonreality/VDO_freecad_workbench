"""Pruebas del visor 2D de coco (CocoPreview2D): huella de pixeles y clic en celda.

Escritas primero sobre HEAD (F-UI-3a), antes de cualquier cambio en
coco_preview2d.py o coco_construccion_widgets.py. El golden SHA-256 se genera
una vez con un script temporal en /tmp bajo freecadcmd y se guarda en
tests/fixtures/coco_preview2d_huella.json. No se regenera despues de escribir el test.
"""

import hashlib
import json
import os
import unittest
from pathlib import Path

from tests.soporte.qt import qapplication
from tests.soporte.requisitos import requiere_freecad, requiere_qt

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from freecad.vdo.core.layout_matriz import Layout, Track
from freecad.vdo.core.layout_resolucion import resolve_layout
from freecad.vdo.qt_compat import QtCore, QtGui, QtWidgets
from freecad.vdo.ui.coco_preview2d import (
    ROLE_KEY,
    ROLE_KIND,
    ROLE_LABEL,
    CocoPreview2D,
)

RAIZ = Path(__file__).resolve().parent.parent
FIXTURE = RAIZ / "tests" / "fixtures" / "coco_preview2d_huella.json"


def _resuelto():
    layout = Layout(columns=[Track("x1"), Track("x2")], rows=[Track("y1")])
    return resolve_layout(layout, inner_w=600, inner_h=500, thickness=18)


def _preview(resuelto):
    preview = CocoPreview2D()
    preview.set_layout(resuelto, outer_w=600, outer_h=500)
    preview.resize(400, 300)
    return preview


@requiere_freecad
@requiere_qt
class CocoPreview2DTests(unittest.TestCase):

    def setUp(self):
        qapplication()

    def test_huella_pixeles_coincide_con_golden(self):
        resuelto = _resuelto()
        preview = _preview(resuelto)
        pixmap = preview.grab()
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, "PNG")
        sha = hashlib.sha256(buffer.data()).hexdigest()
        esperado = json.loads(FIXTURE.read_text(encoding="utf-8"))["sha256"]
        self.assertEqual(sha, esperado)

    def test_clic_en_primera_celda_emite_cellClicked(self):
        resuelto = _resuelto()
        preview = _preview(resuelto)
        scene = preview.scene()
        capturas = []
        preview.cellClicked.connect(capturas.append)
        celdas = [
            item
            for item in scene.items()
            if isinstance(item, QtWidgets.QGraphicsRectItem)
            and item.data(ROLE_KIND) == "cell"
        ]
        self.assertTrue(celdas, "no hay celdas en la escena")
        celda = min(celdas, key=lambda it: it.scenePos().x())
        etiqueta = str(celda.data(ROLE_LABEL) or celda.data(ROLE_KEY))
        pos = preview.mapFromScene(celda.sceneBoundingRect().center())
        evento = QtGui.QMouseEvent(
            QtCore.QEvent.Type.MouseButtonPress,
            pos,
            QtCore.Qt.LeftButton,
            QtCore.Qt.LeftButton,
            QtCore.Qt.NoModifier,
        )
        preview.mousePressEvent(evento)
        self.assertEqual(capturas, [etiqueta])


if __name__ == "__main__":
    unittest.main()
