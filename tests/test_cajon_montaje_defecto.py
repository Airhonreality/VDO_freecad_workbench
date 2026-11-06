"""
tests/test_cajon_montaje_defecto.py
Regresión F1 (D-87): el accept del panel de cajón con la opción por defecto del
montaje de fachada debe guardar el valor del enumerado (parche), no la etiqueta
visible (Parche). Antes de D-87 el accept devolvía False.
"""

import contextlib
import unittest

import FreeCAD as App

from tests.soporte.qt import qapplication
from tests.soporte.requisitos import requiere_freecad

_DOC = "DocMontajeDefectoVDO"
_VALORES = ("parche", "semiparche", "embebida")


@requiere_freecad
class TestCajonMontajeDefecto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        qapplication()

    def setUp(self):
        with contextlib.suppress(BaseException):
            App.closeDocument(_DOC)
        self.doc = App.newDocument(_DOC)
        App.setActiveDocument(self.doc.Name)

    def tearDown(self):
        with contextlib.suppress(BaseException):
            App.closeDocument(_DOC)

    def _cajon(self):
        from freecad.vdo.cad.cajon import make_cajon
        obj = make_cajon(self.doc, {"nombre": "Cajon_F1"})
        self.assertIsNotNone(obj)
        return obj

    def _panel(self, obj):
        from freecad.vdo.ui.cajon_task import CajonTaskPanel
        return CajonTaskPanel(obj=obj, auto_transaction=False)

    def test_accept_con_valores_por_defecto_devuelve_true(self):
        obj = self._cajon()
        panel = self._panel(obj)
        self.assertTrue(panel.accept())
        self.assertEqual(obj.TipoMontaje, "parche")

    def test_cada_montaje_se_guarda_y_se_carga_por_valor(self):
        for valor in _VALORES:
            with self.subTest(montaje=valor):
                obj = self._cajon()
                obj.TipoMontaje = valor
                panel = self._panel(obj)
                self.assertEqual(panel.combo_montaje_fachada.currentData(), valor)
                self.assertTrue(panel.accept())
                self.assertEqual(obj.TipoMontaje, valor)
                self.doc.removeObject(obj.Name)


if __name__ == "__main__":
    unittest.main()
