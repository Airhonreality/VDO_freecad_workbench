"""Pruebas unitarias de los nuevos tipos de FormBuilder (F-UI-1).

Puro Qt: corren en nivel 1 con PySide disponible (QT_QPA_PLATFORM=offscreen).
No modifican el comportamiento existente de FormBuilder.
"""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from freecad.vdo.qt_compat import QtWidgets
from freecad.vdo.ui.form_builder import FormBuilder
from tests.soporte.qt import qapplication
from tests.soporte.requisitos import requiere_qt


@requiere_qt
class FormBuilderTiposTests(unittest.TestCase):

    def setUp(self):
        qapplication()
        self.builder = FormBuilder()

    def test_construir_fila_horizontal(self):
        layout = QtWidgets.QHBoxLayout()
        campos = [
            {"tipo": "double_spin", "clave": "ancho", "valor_defecto": 600, "sufijo": " W", "rango": (0, 10000)},
            {"tipo": "double_spin", "clave": "alto", "valor_defecto": 720, "sufijo": " H", "rango": (0, 10000)},
            {"tipo": "double_spin", "clave": "fondo", "valor_defecto": 580, "sufijo": " D", "rango": (0, 10000)},
        ]
        claves = self.builder.construir_fila(layout, campos, separador="×")  # noqa: RUF001

        self.assertEqual(claves, ["ancho", "alto", "fondo"])
        self.assertEqual(layout.count(), 5)

        widgets = [layout.itemAt(i).widget() for i in range(layout.count())]
        self.assertIsInstance(widgets[0], QtWidgets.QDoubleSpinBox)
        self.assertIsInstance(widgets[1], QtWidgets.QLabel)
        self.assertEqual(widgets[1].text(), "×")  # noqa: RUF001
        self.assertIsInstance(widgets[2], QtWidgets.QDoubleSpinBox)
        self.assertIsInstance(widgets[3], QtWidgets.QLabel)
        self.assertEqual(widgets[3].text(), "×")  # noqa: RUF001
        self.assertIsInstance(widgets[4], QtWidgets.QDoubleSpinBox)

        self.assertEqual(widgets[0].suffix(), " W")
        self.assertEqual(widgets[2].suffix(), " H")
        self.assertEqual(widgets[4].suffix(), " D")
        self.assertEqual(widgets[0].value(), 600)
        self.assertEqual(widgets[2].value(), 720)
        self.assertEqual(widgets[4].value(), 580)

        # Los sub-campos quedan registrados para builder.widget(clave).
        self.assertIs(self.builder.widget("ancho"), widgets[0])
        self.assertIs(self.builder.widget("alto"), widgets[2])
        self.assertIs(self.builder.widget("fondo"), widgets[4])

    def test_ancho_fijo(self):
        w = self.builder.crear(
            {"tipo": "double_spin", "clave": "x", "valor_defecto": 0, "ancho_fijo": 64}
        )
        self.assertEqual(w.maximumWidth(), 64)

    def test_boton(self):
        w = self.builder.crear(
            {"tipo": "boton", "clave": "btn", "texto": "➗ Aplicar Subdivisión"}
        )
        self.assertIsInstance(w, QtWidgets.QPushButton)
        self.assertEqual(w.text(), "➗ Aplicar Subdivisión")


if __name__ == "__main__":
    unittest.main()
